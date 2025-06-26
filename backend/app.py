# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime, timedelta
import string
import random
import uvicorn
from typing import Optional, Dict, Any, List
import re
import json
# Import logging middleware
from middleware.logging_middleware import LoggingMiddleware

# FastAPI App
app = FastAPI()

# Add logging middleware correctly
app.add_middleware(LoggingMiddleware)

# Create a separate logger instance for manual logging
class SimpleLogger:
    def __init__(self):
        self.log_events = []
    
    def log_event(self, event_type, data):
        """Log custom events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        print(f"[EVENT] {json.dumps(log_entry)}")
        self.log_events.append(log_entry)
    
    def log_error(self, error_type, message):
        """Log errors"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message
        }
        print(f"[ERROR] {json.dumps(log_entry)}")
        self.log_events.append(log_entry)

# Create logger instance for manual logging
logger = SimpleLogger()

# In-memory storage
url_storage: Dict[str, Dict[str, Any]] = {}
stats_storage: Dict[str, Dict[str, Any]] = {}
used_shortcodes: set = set()

# Pydantic Models
class URLCreateRequest(BaseModel):
    url: HttpUrl
    validity: Optional[int] = 30
    shortcode: Optional[str] = None
    
    @validator('validity')
    def validate_validity(cls, v):
        if v <= 0:
            raise ValueError('Validity must be greater than 0')
        return v
    
    @validator('shortcode')
    def validate_shortcode(cls, v):
        if v is not None:
            if len(v) < 4:
                raise ValueError('Shortcode must be at least 4 characters long')
            if not re.match(r'^[a-zA-Z0-9]+$', v):
                raise ValueError('Shortcode can only contain alphanumeric characters')
        return v

class URLCreateResponse(BaseModel):
    shortLink: str
    expiry: str

class ClickData(BaseModel):
    timestamp: str
    source: str
    user_agent: str
    ip: str
    geographical_info: Optional[str] = None

class URLStatsResponse(BaseModel):
    shortcode: str
    original_url: str
    total_clicks: int
    created_at: str
    expiry: str
    clicks_data: List[ClickData]
    is_expired: bool

# Helper Functions
def generate_shortcode() -> str:
    """Generate a unique 6-character shortcode"""
    for _ in range(100):
        shortcode = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if shortcode not in used_shortcodes:
            used_shortcodes.add(shortcode)
            return shortcode
    raise HTTPException(status_code=500, detail="Unable to generate unique shortcode")

def get_geographical_info(ip: str) -> str:
    """Basic geographical information"""
    if ip in ["127.0.0.1", "localhost"]:
        return "Localhost"
    return "Unknown Location"

# API Endpoints
@app.post("/shorturls", status_code=201, response_model=URLCreateResponse)
async def create_short_url(request: URLCreateRequest):
    """Create a new shortened URL"""
    
    try:
        url_str = str(request.url)
        
        # Handle custom shortcode
        if request.shortcode:
            if request.shortcode in used_shortcodes:
                logger.log_error("SHORTCODE_EXISTS", f"Shortcode already exists: {request.shortcode}")
                raise HTTPException(status_code=400, detail="Shortcode already exists")
            shortcode = request.shortcode
            used_shortcodes.add(shortcode)
        else:
            shortcode = generate_shortcode()
        
        # Calculate expiry
        expiry_time = datetime.now() + timedelta(minutes=request.validity)
        
        # Store URL data
        url_storage[shortcode] = {
            "url": url_str,
            "created_at": datetime.now().isoformat(),
            "expiry": expiry_time.isoformat(),
            "clicks": 0
        }
        
        # Initialize stats
        stats_storage[shortcode] = {
            "total_clicks": 0,
            "clicks_data": [],
            "original_url": url_str,
            "created_at": datetime.now().isoformat(),
            "expiry": expiry_time.isoformat()
        }
        
        # Log URL creation
        logger.log_event("URL_CREATED", {
            "shortcode": shortcode,
            "url": url_str,
            "validity": request.validity
        })
        
        return URLCreateResponse(
            shortLink=f"http://hostname:port/{shortcode}",
            expiry=expiry_time.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("URL_CREATION_FAILED", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{shortcode}")
async def redirect_short_url(shortcode: str, request: Request):
    """Redirect to original URL"""
    
    try:
        # Check if shortcode exists
        if shortcode not in url_storage:
            logger.log_error("SHORTCODE_NOT_FOUND", f"Shortcode not found: {shortcode}")
            raise HTTPException(status_code=404, detail="Short URL not found")
        
        url_data = url_storage[shortcode]
        
        # Check if expired
        expiry_time = datetime.fromisoformat(url_data["expiry"])
        if datetime.now() > expiry_time:
            logger.log_error("URL_EXPIRED", f"URL expired: {shortcode}")
            raise HTTPException(status_code=410, detail="Short URL has expired")
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        referer = request.headers.get("referer", "direct")
        
        # Update click count
        url_storage[shortcode]["clicks"] += 1
        
        # Record click data
        click_data = {
            "timestamp": datetime.now().isoformat(),
            "source": referer,
            "user_agent": user_agent,
            "ip": client_ip,
            "geographical_info": get_geographical_info(client_ip)
        }
        
        stats_storage[shortcode]["total_clicks"] += 1
        stats_storage[shortcode]["clicks_data"].append(click_data)
        
        # Log redirect
        logger.log_event("URL_REDIRECT", {
            "shortcode": shortcode,
            "destination": url_data['url'],
            "client_ip": client_ip
        })
        
        return RedirectResponse(url=url_data["url"], status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("REDIRECT_FAILED", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/shorturls/{shortcode}", response_model=URLStatsResponse)
async def get_short_url_stats(shortcode: str):
    """Get statistics for a shortened URL"""
    
    try:
        if shortcode not in stats_storage:
            logger.log_error("STATS_NOT_FOUND", f"Stats not found for: {shortcode}")
            raise HTTPException(status_code=404, detail="Short URL not found")
        
        stats = stats_storage[shortcode]
        
        # Check if expired
        expiry_time = datetime.fromisoformat(stats["expiry"])
        is_expired = datetime.now() > expiry_time
        
        # Convert click data
        clicks_data = [
            ClickData(
                timestamp=click["timestamp"],
                source=click["source"],
                user_agent=click["user_agent"],
                ip=click["ip"],
                geographical_info=click.get("geographical_info")
            )
            for click in stats["clicks_data"]
        ]
        
        # Log stats access
        logger.log_event("STATS_ACCESSED", {
            "shortcode": shortcode,
            "total_clicks": stats["total_clicks"]
        })
        
        return URLStatsResponse(
            shortcode=shortcode,
            original_url=stats["original_url"],
            total_clicks=stats["total_clicks"],
            created_at=stats["created_at"],
            expiry=stats["expiry"],
            clicks_data=clicks_data,
            is_expired=is_expired
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("STATS_FAILED", str(e))
        raise HTTPException(status_code=500, detail="Unable to retrieve statistics")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)