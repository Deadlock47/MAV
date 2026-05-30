# 🎨 Manhwa Metadata API

A FastAPI-based REST API to extract and serve manhwa metadata from HTML files.

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API Server
```bash
python manhwa_api.py
```

Or using uvicorn directly:
```bash
uvicorn manhwa_api:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### 1. **Get Full Metadata**
Extract complete manhwa metadata from HTML file

**Endpoint:** `GET /api/manhwa/metadata`

**Parameters:**
- `file` (optional): HTML file path (default: `output.html`)

**Example Request:**
```bash
curl "http://localhost:8000/api/manhwa/metadata"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "title": "I Became an Apartment Manager (Official)",
    "alternative_names": "I Became the Apartment Manager, Apateu Gwalliini Doeeotda, ...",
    "poster_url": "https://cdn.mangadistrict.com/thumbnail/i-became-an-apartment-manager-official.webp",
    "rating": "4.3",
    "total_ratings": "6",
    "description": "Sleep with the women living in this building—whether through blackmail, seduction, or even force. Hans Lee accepts the sweet but dangerous offer...",
    "authors": ["Bibik"],
    "artists": ["Beluga"],
    "publication_type": "Manhwa, Webtoons",
    "genres": [
      "Borderline H",
      "Drama",
      "Explicit Sex",
      "Full Color",
      "Harem",
      "Manhwa",
      "Sexual Abuse",
      "Webtoons"
    ],
    "tags": [
      "Borderline H",
      "Drama",
      "Explicit Sex",
      "Forced",
      "Full Color",
      "Harem",
      "Humiliating",
      "Manhwa",
      "MILF",
      "NTL",
      "Reverse NTR",
      "Sexual Abuse",
      "Taming",
      "Webtoons"
    ],
    "status": "OnGoing",
    "year_published": "2025",
    "published_by": "Manga District",
    "number_of_chapters": 35,
    "all_chapters": [
      {
        "title": "Chapter 35 - Carly Park, the pervert of our apartment",
        "url": "https://mangadistrict.com/series/i-became-an-apartment-manager-official/chapter-35/"
      },
      {
        "title": "Chapter 34 - Did she come to the convenience store with a dildo in",
        "url": "https://mangadistrict.com/series/i-became-an-apartment-manager-official/chapter-34/"
      }
      // ... more chapters
    ]
  }
}
```

---

### 2. **Get Chapters Only**
Get only the chapters list from the HTML

**Endpoint:** `GET /api/manhwa/chapters`

**Parameters:**
- `file` (optional): HTML file path (default: `output.html`)

**Example Request:**
```bash
curl "http://localhost:8000/api/manhwa/chapters"
```

**Example Response:**
```json
{
  "success": true,
  "title": "I Became an Apartment Manager (Official)",
  "total_chapters": 35,
  "chapters": [
    {
      "title": "Chapter 35 - Carly Park, the pervert of our apartment",
      "url": "https://mangadistrict.com/series/i-became-an-apartment-manager-official/chapter-35/"
    },
    {
      "title": "Chapter 34 - Did she come to the convenience store with a dildo in",
      "url": "https://mangadistrict.com/series/i-became-an-apartment-manager-official/chapter-34/"
    }
    // ... more chapters
  ]
}
```

---

### 3. **Get Summary Only**
Get only the title, description, and rating

**Endpoint:** `GET /api/manhwa/summary`

**Parameters:**
- `file` (optional): HTML file path (default: `output.html`)

**Example Request:**
```bash
curl "http://localhost:8000/api/manhwa/summary"
```

**Example Response:**
```json
{
  "success": true,
  "title": "I Became an Apartment Manager (Official)",
  "description": "Sleep with the women living in this building—whether through blackmail, seduction, or even force. Hans Lee accepts the sweet but dangerous offer that could turn his miserable life upside down… Apartment 301, the married woman Suzy Han. I need to find this woman's weakness fast!",
  "rating": "4.3",
  "total_ratings": "6"
}
```

---

### 4. **Health Check**
Check if the API is running

**Endpoint:** `GET /health`

**Example Request:**
```bash
curl "http://localhost:8000/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "service": "Manhwa Metadata API"
}
```

---

### 5. **Root Endpoint**
Get information about available endpoints

**Endpoint:** `GET /`

**Example Request:**
```bash
curl "http://localhost:8000/"
```

**Example Response:**
```json
{
  "message": "Welcome to Manhwa Metadata API",
  "endpoints": {
    "metadata": "/api/manhwa/metadata",
    "docs": "/docs"
  }
}
```

---

## 🔧 Usage Examples

### Python
```python
import requests
import json

# Fetch full metadata
response = requests.get("http://localhost:8000/api/manhwa/metadata")
data = response.json()

print(json.dumps(data, indent=2))

# Access specific fields
metadata = data['data']
print(f"Title: {metadata['title']}")
print(f"Authors: {metadata['authors']}")
print(f"Chapters: {metadata['number_of_chapters']}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function getManhwaMetadata() {
  try {
    const response = await axios.get('http://localhost:8000/api/manhwa/metadata');
    const metadata = response.data.data;
    
    console.log('Title:', metadata.title);
    console.log('Authors:', metadata.authors);
    console.log('Genres:', metadata.genres);
    console.log('Total Chapters:', metadata.number_of_chapters);
  } catch (error) {
    console.error('Error:', error);
  }
}

getManhwaMetadata();
```

### cURL
```bash
# Get full metadata
curl "http://localhost:8000/api/manhwa/metadata"

# Get chapters only
curl "http://localhost:8000/api/manhwa/chapters"

# Get summary only
curl "http://localhost:8000/api/manhwa/summary"

# Specify custom HTML file
curl "http://localhost:8000/api/manhwa/metadata?file=custom_output.html"
```

---

## 📋 Extracted Metadata Fields

The API extracts the following information:

| Field | Description | Type |
|-------|-------------|------|
| `title` | Manhwa title | String |
| `alternative_names` | Alternative titles/names | String |
| `poster_url` | URL to cover image | String |
| `rating` | Average rating | String |
| `total_ratings` | Number of ratings | String |
| `description` | Full description/summary | String |
| `authors` | List of authors | Array |
| `artists` | List of artists/illustrators | Array |
| `publication_type` | Type (Manhwa, Webtoons, etc.) | String |
| `genres` | List of genres | Array |
| `tags` | List of tags | Array |
| `status` | Status (OnGoing/Finished) | String |
| `year_published` | Publication year | String |
| `published_by` | Publisher name | String |
| `number_of_chapters` | Total chapter count | Integer |
| `all_chapters` | Array of chapters with URLs | Array |

---

## 🔄 Integration with Existing App

If you have an existing FastAPI app (`app.py`), you can include this API:

```python
from manhwa_api import app as manhwa_app

# In your main app.py
app.include_router(manhwa_app.router, prefix="/api")
```

---

## 📦 Requirements

- Python 3.7+
- fastapi
- uvicorn[standard]
- beautifulsoup4
- duckdb (optional, for future database integration)

Install with:
```bash
pip install -r requirements.txt
```

---

## 🎯 Features

✅ Extracts all manhwa metadata from HTML  
✅ Returns formatted JSON responses  
✅ Multiple endpoint options for different use cases  
✅ Automatic API documentation (Swagger UI)  
✅ Error handling with proper HTTP status codes  
✅ CORS enabled for cross-origin requests  
✅ Health check endpoint  
✅ Support for custom HTML file paths  

---

## 📝 Notes

- The API expects HTML files in the same format as the Manga District website
- Default HTML file: `output.html` in the same directory
- All responses include a `success` boolean field
- Errors return appropriate HTTP status codes (404 for file not found, 500 for parsing errors)

---

## 🚀 Deployment

### Using Uvicorn
```bash
uvicorn manhwa_api:app --host 0.0.0.0 --port 8000
```

### Using Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker manhwa_api:app
```

---

## 📧 Support

For issues or questions, check the API documentation at `/docs` or `/redoc`
