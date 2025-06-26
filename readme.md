# 🔗 AffordMed URL Shortener

A fast, reliable, and feature-rich URL shortener API built with **FastAPI** and **Python**. Transform long URLs into short, shareable links with advanced analytics and customization options.

## ✨ Features

- **🚀 Lightning Fast**: Built on FastAPI for high performance
- **🎯 Custom Short Codes**: Create personalized short links
- **⏰ Expiration Control**: Set custom validity periods (minutes)
- **📊 Detailed Analytics**: Track clicks with comprehensive statistics
- **🌍 Geographic Tracking**: Basic location information for clicks
- **🔒 Robust Validation**: Input validation and error handling
- **📝 Request Logging**: Comprehensive logging middleware
- **🏥 Health Monitoring**: Built-in health check endpoint
- **🌐 CORS Support**: Cross-origin request handling

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104.1
- **Runtime**: Python 3.12+
- **Server**: Uvicorn 0.24.0
- **Validation**: Pydantic 2.5.0
- **Package Manager**: Poetry

## 📋 Prerequisites

- Python 3.12 or higher
- Poetry (for dependency management)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/NarasimhaSaladi/22P31A4234
cd affordmed
```

### 2. Install Dependencies

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 3. Activate Virtual Environment

```bash
poetry shell
```

### 4. Run the Application

```bash
# Using Poetry
poetry run python backend/app.py

# Or directly with uvicorn
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔧 API Endpoints

### Create Short URL
```http
POST /shorturls
```

**Request Body:**
```json
{
  "url": "https://example.com/very-long-url",
  "validity": 30,
  "shortcode": "custom123"
}
```

**Response:**
```json
{
  "shortLink": "http://localhost:8000/abc123",
  "expiry": "2024-12-01T10:30:00"
}
```

### Redirect to Original URL
- **GET** `/{shortcode}`
- **Description**: Redirect to the original URL and track analytics
- **Response**: 302 redirect to original URL
- **⚠️ Important**: Use browser or curl for testing redirects. The Swagger UI may show CORS errors due to redirect handling limitations.


### Get URL Statistics
```http
GET /shorturls/{shortcode}
```

**Response:**
```json
{
  "shortcode": "abc123",
  "original_url": "https://example.com",
  "total_clicks": 42,
  "created_at": "2024-11-01T10:00:00",
  "expiry": "2024-12-01T10:30:00",
  "clicks_data": [
    {
      "timestamp": "2024-11-01T11:15:00",
      "source": "direct",
      "user_agent": "Mozilla/5.0...",
      "ip": "192.168.1.1",
      "geographical_info": "Unknown Location"
    }
  ],
  "is_expired": false
}
```

### Health Check
```http
GET /health
```

## 💡 Usage Examples

### Using cURL

**Create a short URL:**
```bash
curl -X POST "http://localhost:8000/shorturls" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/NarasimhaSaladi/22P31A4234",
    "validity": 60,
    "shortcode": "github"
  }'
```

**Get statistics:**
```bash
curl "http://localhost:8000/shorturls/github"
```

### Using Python

```python
import requests

# Create short URL
response = requests.post("http://localhost:8000/shorturls", json={
    "url": "https://docs.python.org",
    "validity": 120
})

data = response.json()
print(f"Short URL: {data['shortLink']}")
```

## ⚙️ Configuration

### Custom Validity Period
- Default: 30 minutes
- Range: Any positive integer (minutes)
- Example: Set `"validity": 1440` for 24 hours

### Custom Short Codes
- Minimum length: 4 characters
- Allowed characters: Alphanumeric only (a-z, A-Z, 0-9)
- Must be unique

## 📊 Analytics Features

Track comprehensive click data including:
- **Timestamp**: When the link was clicked
- **Source**: Referrer information
- **User Agent**: Browser/client information
- **IP Address**: Client IP (for geographic tracking)
- **Geographic Info**: Basic location data
- **Total Clicks**: Aggregate click count

## 🔍 Logging

The application includes comprehensive logging for:
- Request/Response cycles
- URL creation events
- Redirect activities
- Error tracking
- Statistics access

Logs are printed to console in JSON format for easy parsing.

## 🛡️ Error Handling

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request (invalid input, duplicate shortcode) |
| 404 | Short URL not found |
| 410 | Short URL has expired |
| 500 | Internal server error |

## 🚧 Development

### Project Structure
```
affordmed/
├── .venv/                # Virtual environment (Poetry managed)
├── backend/
│   ├── __pycache__/     # Python cache files
│   └── app.py           # Main FastAPI application
├── frontend/            # Frontend directory (currently empty - planned for future UI)
├── middleware/
│   ├── __pycache__/     # Python cache files
│   └── logging_middleware.py  # Request logging middleware
├── poetry.lock          # Poetry lock file
├── pyproject.toml       # Poetry configuration & dependencies
└── README.md           # This documentation
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## 📝 TODO / Roadmap

- [ ] **Frontend Development**: Build a React/Vue.js web interface for the URL shortener
- [ ] Persistent storage (database integration)
- [ ] User authentication and management
- [ ] Bulk URL creation
- [ ] Advanced analytics dashboard
- [ ] Rate limiting
- [ ] Custom domains
- [ ] QR code generation
- [ ] API key authentication

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Narasimha Saladi**  
📧 narasimhasaladi7@gmail.com

---

⭐ **Star this repository if you found it helpful!**

> Built with ❤️ using FastAPI and Python