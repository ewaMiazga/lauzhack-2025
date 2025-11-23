# 🔥 FireDoc VLM - Satellite Burn Assessment Tool

A Vision-Language Model powered tool for analyzing satellite imagery to assess wildfire burn severity and environmental impact.

## 📋 Project Overview

**FireDoc VLM** combines satellite imagery with AI vision models to help analyze burn areas from wildfires. Users can:
1. Select regions on an interactive map
2. Choose date ranges and data layers (NBR, NDVI, SWIR, etc.)
3. Ask questions about the satellite imagery
4. Get AI-powered analysis of burn severity and environmental impact

### Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Leaflet.js for interactive maps
- Leaflet Draw for region selection

**Backend:**
- Python 3.x
- Flask web framework
- Together AI Vision API (Llama-Vision-Free model)
- Copernicus API for satellite data

## 🏗️ Project Structure

```
lauzhack-2025/
├── index.html              # Main web interface
├── app.js                  # Frontend JavaScript logic
├── styles.css              # Styling and layout
├── backend.py              # Flask API server (MAIN BACKEND)
├── together-main.py        # Together AI vision demo
├── api-copernicus.py       # Copernicus satellite data fetcher
├── requirements.txt        # Python dependencies
├── images/                 # Test images directory
│   └── car.jpg            # Sample image for testing
└── satellite_data/         # Satellite imagery storage
    └── sentinel2_*.jpg    # Downloaded satellite images
```

## 🔄 How It Works

### Architecture Flow:

```
┌─────────────┐      HTTP Requests      ┌──────────────┐
│  Frontend   │ ───────────────────────> │   Backend    │
│  (Browser)  │                          │   (Flask)    │
│             │ <─────────────────────── │              │
└─────────────┘      JSON Responses      └──────────────┘
     │                                          │
     │ 1. User selects region                  │
     │ 2. User clicks "Fetch Data"             │ 3. Fetches satellite
     │                                          │    image from storage
     │ 4. User asks question                   │
     │ 5. Sends prompt + context               │ 6. Encodes image to base64
     │                                          │ 7. Calls Together AI API
     │ 8. Receives AI analysis                 │
     │                                          ▼
     │                                   ┌──────────────┐
     │                                   │  Together AI │
     │                                   │  Vision API  │
     │                                   └──────────────┘
```

### Detailed Flow:

1. **Frontend (app.js)**:
   - User draws a rectangle on the map to select a region
   - Coordinates are stored in `appState.selectedRegion`
   - User selects date range and data layers
   - Clicks "Fetch Satellite Data" button

2. **Backend (/api/fetch-data)**:
   - Receives region coordinates and date range
   - Checks for available satellite images
   - Returns list of available images

3. **Frontend Analysis**:
   - User types a question in the prompt box
   - Clicks "Analyze with VLM"
   - Sends prompt along with region context

4. **Backend (/api/analyze)**:
   - Receives the prompt and context
   - Loads the satellite image from `satellite_data/`
   - Encodes image to base64
   - Builds enhanced prompt with geographic context
   - Calls Together AI Vision API
   - Streams response back to frontend

5. **AI Response**:
   - Vision model analyzes the satellite imagery
   - Provides detailed assessment of burn severity
   - Frontend displays the response in chat interface

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```env
TOGETHER_API_KEY=your_together_ai_api_key_here
```

Get your API key from: https://api.together.xyz/

### 3. Add Satellite Images

Place satellite imagery (JPEG/PNG) in the `satellite_data/` directory:

```bash
satellite_data/
├── sentinel2_20231007.jpg
├── sentinel2_20231015.jpg
└── ...
```

You can use `api-copernicus.py` to download real satellite data from Copernicus.

### 4. Run the Backend Server

```bash
python backend.py
```

The server will start on `http://localhost:5000`

### 5. Open the Frontend

Open your browser and navigate to:
```
http://localhost:5000
```

## 🎯 Usage Guide

### Basic Workflow:

1. **Select a Region**:
   - Click the rectangle tool on the map
   - Draw a box around your area of interest
   - See coordinates displayed in the sidebar

2. **Configure Settings**:
   - Set start and end dates
   - Choose data layers (NBR, NDVI, etc.)

3. **Fetch Data**:
   - Click "🚀 Fetch Satellite Data"
   - Wait for confirmation message

4. **Ask Questions**:
   - Type your question in the prompt box
   - Examples:
     - "Analyze the burn severity in this region"
     - "What's the vegetation recovery rate?"
     - "Estimate the total burned area"
   - Click "✨ Analyze with VLM"

5. **Review Analysis**:
   - Read the AI's detailed response
   - Continue asking follow-up questions

## 📡 API Endpoints

### GET `/api/health`
Check server health and configuration

**Response:**
```json
{
  "status": "healthy",
  "together_api_configured": true,
  "satellite_data_dir": "/path/to/satellite_data",
  "images_available": 5
}
```

### POST `/api/fetch-data`
Fetch satellite data for a region

**Request:**
```json
{
  "region": {
    "north": 46.0,
    "south": 45.5,
    "east": 13.5,
    "west": 13.0
  },
  "dateRange": {
    "start": "2023-10-01",
    "end": "2023-10-31"
  },
  "layers": ["truecolor", "nbr", "ndvi"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Found 3 satellite image(s)",
  "images": ["sentinel2_20231007.jpg", "..."]
}
```

### POST `/api/analyze`
Analyze satellite imagery with Vision AI

**Request:**
```json
{
  "prompt": "What is the burn severity?",
  "region": {...},
  "dateRange": {...},
  "layers": [...],
  "conversationHistory": [...]
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on the satellite imagery...",
  "image_analyzed": "sentinel2_20231007.jpg"
}
```

### GET `/api/test-car-image`
Test endpoint to verify vision API with car.jpg

**Response:**
```json
{
  "success": true,
  "response": "The car appears to be a..."
}
```

## 🧪 Testing the Vision API

To test the Together AI vision capability with the sample car image:

### Option 1: Use the test endpoint
```bash
curl http://localhost:5000/api/test-car-image
```

### Option 2: Run the standalone script
```bash
python together-main.py
```

This will analyze `images/car.jpg` and tell you the car brand.

## 🔧 Code Structure Explained

### `backend.py` - Main Server

**Key Functions:**

- `encode_image_to_base64(image_path)`: Converts images to base64 for API transmission
- `analyze_image_with_vlm(image_path, prompt, conversation_history)`: Calls Together AI Vision API
- `/api/fetch-data`: Handles satellite data retrieval requests
- `/api/analyze`: Processes AI analysis requests

### `app.js` - Frontend Logic

**Key Components:**

- `appState`: Global state management for selected region, dates, layers
- `initMap()`: Initializes Leaflet map with drawing controls
- `handlePromptSubmission()`: Sends prompts to backend for analysis
- `addUserMessage()`, `addAIMessage()`: Manages chat UI

### `together-main.py` - Vision API Demo

Standalone script demonstrating Together AI vision capabilities:
- Loads an image (car.jpg)
- Encodes to base64
- Sends to vision model
- Streams response

## 🌟 Features

✅ **Interactive Map Interface**: Draw regions directly on the map
✅ **Date Range Selection**: Choose time periods for analysis
✅ **Multiple Data Layers**: Support for NBR, NDVI, SWIR, FIRMS
✅ **AI-Powered Analysis**: Vision-Language Model analyzes imagery
✅ **Conversation History**: Follow-up questions with context
✅ **Real-time Streaming**: AI responses stream in real-time
✅ **Clean UI**: Modern, responsive design

## 🔮 Future Enhancements

- [ ] Direct Copernicus API integration for live data fetching
- [ ] Multiple image comparison (before/after)
- [ ] Export analysis reports as PDF
- [ ] Integration with additional satellite data sources
- [ ] Custom layer visualization on the map
- [ ] User authentication and saved analyses
- [ ] Batch processing for multiple regions

## 🐛 Troubleshooting

**Issue: API key not found**
```
Solution: Create .env file with TOGETHER_API_KEY=your_key
```

**Issue: No satellite images available**
```
Solution: Add JPEG/PNG images to satellite_data/ directory
```

**Issue: CORS errors in browser**
```
Solution: Ensure flask-cors is installed and backend is running
```

**Issue: Image analysis fails**
```
Solution: Check that image file exists and is a valid JPEG/PNG
```

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

This project was created for LauzHack 2025. Feel free to fork and improve!

---

**Built with ❤️ for wildfire assessment and environmental monitoring**

