# middleware/logging_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime
import json

# Global logger instance for sharing between middleware and manual logging
class GlobalLogger:
    def __init__(self):
        self.log_events = []
    
    def log_request(self, log_data):
        """Log request data"""
        print(f"[REQUEST] {json.dumps(log_data)}")
        self.log_events.append(log_data)
    
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

# Create global logger instance
global_logger = GlobalLogger()

class LoggingMiddleware(BaseHTTPMiddleware):
    """Simple logging middleware for FastAPI"""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        
        # Log request
        log_entry = {
            "timestamp": start_time.isoformat(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        global_logger.log_request(log_entry)
        
        # Process the request
        response = await call_next(request)
        
        # Log response
        process_time = (datetime.now() - start_time).total_seconds()
        global_logger.log_event("REQUEST_COMPLETED", {
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time
        })
        
        return response