# 🔥 FireDoc VLM - Project Summary & Technical Documentation

## 📊 Project Understanding

**FireDoc VLM** is a web-based satellite burn assessment tool that combines:
- **Interactive mapping** for region selection
- **Satellite imagery** from Copernicus/Sentinel-2
- **Vision AI** from Together AI to analyze burn severity

### What Problem Does It Solve?

After wildfires, environmental agencies need to quickly assess:
- Burn severity and extent
- Vegetation health and recovery patterns
- Environmental impact
- Areas requiring immediate attention

Traditional analysis is slow and requires expert knowledge. FireDoc VLM democratizes this using AI.

---

## 🏗️ Architecture Overview

### Three-Tier Architecture:

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│  (HTML + CSS + JavaScript + Leaflet.js)                 │
│                                                          │
│  Components:                                            │
│  - Interactive map with drawing tools                   │
│  - Control panel (date range, layers)                   │
│  - Chat interface for AI interaction                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ HTTP/JSON (Port 5000)
                   │
┌──────────────────▼──────────────────────────────────────┐
│                    BACKEND (Flask)                       │
│                   backend.py                             │
│                                                          │
│  Endpoints:                                             │
│  - /api/fetch-data    (Get satellite images)           │
│  - /api/analyze       (AI vision analysis)             │
│  - /api/health        (Server status)                  │
│  - /api/test-car-image (Test vision API)               │
└──────────────────┬──────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
         ▼                    ▼
┌─────────────────┐   ┌──────────────────┐
│  Together AI    │   │  File System     │
│  Vision API     │   │  (satellite_data)│
│  (Llama-Vision) │   │  (images)        │
└─────────────────┘   └──────────────────┘
```

---

## 📁 File-by-File Explanation

### 1. `index.html` - Frontend UI

**Purpose:** Main web interface for the application

**Key Components:**
- **Header:** Branding and title
- **Map Section:** Leaflet.js interactive map with drawing tools
- **Control Panel:**
  - Date range selector
  - Layer toggles (NBR, NDVI, SWIR, etc.)
  - Region info display
  - "Fetch Data" button
- **Analysis Section:**
  - Prompt input textarea
  - "Analyze with VLM" button
  - Response area (chat interface)

**Libraries Used:**
- Leaflet.js 1.9.4 - Interactive mapping
- Leaflet Draw 1.0.4 - Drawing rectangles on map

---

### 2. `app.js` - Frontend Logic

**Purpose:** Client-side JavaScript handling user interactions and API calls

**Global State (`appState` object):**
```javascript
{
    selectedRegion: {north, south, east, west},  // Map coordinates
    selectedLayers: ['layer-truecolor', ...],    // Active data layers
    startDate: "2023-10-01",                      // Date range start
    endDate: "2023-10-31",                        // Date range end
    conversationHistory: [...]                    // Chat messages
}
```

**Key Functions:**

1. **`initMap()`**
   - Creates Leaflet map centered on Switzerland
   - Adds OpenStreetMap tile layer
   - Sets up drawing controls for rectangles
   - Handles draw events (created, edited, deleted)

2. **`updateRegionInfo()`**
   - Displays selected region coordinates
   - Calculates approximate area in km²

3. **`handlePromptSubmission()`**
   - Sends user's question to `/api/analyze`
   - Includes region context and conversation history
   - Updates chat UI with response

4. **`addUserMessage()` / `addAIMessage()`**
   - Manages chat interface
   - Animates new messages
   - Auto-scrolls to latest

**API Communication:**
```javascript
// Example: Fetching satellite data
fetch('/api/fetch-data', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        region: {north, south, east, west},
        dateRange: {start, end},
        layers: ['truecolor', 'nbr']
    })
})
```

---

### 3. `styles.css` - Styling

**Purpose:** Modern, responsive styling for the web interface

**Design System:**
- **Primary Color:** `#ff6b35` (Orange - fire theme)
- **Secondary Color:** `#004e89` (Blue - professional)
- **Accent Color:** `#1a936f` (Green - vegetation)

**Layout:**
- CSS Grid for main content (map + control panel)
- Flexbox for control sections
- Responsive breakpoints for mobile

**Notable Features:**
- Smooth animations on messages
- Custom scrollbar styling
- Loading dots animation
- Gradient buttons with hover effects

---

### 4. `backend.py` - Flask Server (MAIN BACKEND)

**Purpose:** Core server connecting frontend with AI and data sources

**Architecture:**

```python
Flask App
├── Route: / (serve index.html)
├── Route: /<path> (serve static files)
├── Route: /api/health (server status)
├── Route: /api/fetch-data (get satellite images)
├── Route: /api/analyze (AI vision analysis)
└── Route: /api/test-car-image (test endpoint)
```

**Key Functions:**

1. **`encode_image_to_base64(image_path)`**
   ```python
   # Reads image file and converts to base64 string
   # Required format for Together AI Vision API
   with open(image_path, "rb") as f:
       return base64.b64encode(f.read()).decode("utf-8")
   ```

2. **`analyze_image_with_vlm(image_path, prompt, history)`**
   ```python
   # Core AI function
   # 1. Encodes image to base64
   # 2. Builds message structure with conversation history
   # 3. Calls Together AI Vision API
   # 4. Streams response back
   
   stream = together_client.chat.completions.create(
       model="meta-llama/Llama-Vision-Free",
       messages=[...],
       stream=True
   )
   ```

3. **`/api/analyze` endpoint**
   - Receives user prompt and region context
   - Enhances prompt with geographic metadata
   - Loads appropriate satellite image
   - Calls vision AI
   - Returns detailed analysis

**Enhanced Prompt Template:**
```python
f"""You are FireDoc VLM, an expert AI for analyzing satellite imagery.

User's Question: {prompt}

Context:
- Region Coordinates: N{north}°, S{south}°, E{east}°, W{west}°
- Date Range: {start} to {end}
- Data Layers: {layers}

Please analyze the image focusing on:
- Burn severity (if applicable)
- Vegetation health and recovery
- Environmental impact assessment
- Visible patterns or anomalies
"""
```

**CORS Configuration:**
- Enabled via `flask-cors`
- Allows frontend to make cross-origin requests
- Essential for local development

---

### 5. `together-main.py` - Vision API Demo

**Purpose:** Standalone script demonstrating Together AI vision capabilities

**What It Does:**
1. Loads `images/car.jpg`
2. Encodes to base64
3. Sends to Together AI Vision API
4. Asks: "What car brand is it?"
5. Streams response to console

**Usage:**
```bash
python together-main.py
```

**Key Learning:**
- Shows how to structure vision API requests
- Demonstrates streaming responses
- Tests API key configuration

---

### 6. `api-copernicus.py` - Satellite Data Fetcher

**Purpose:** Download satellite imagery from Copernicus Data Space

**What It Does:**
1. Defines area of interest (bounding box)
2. Queries Sentinel-2 satellite data
3. Filters by date range and cloud cover
4. Downloads processed JPEG images

**Current Configuration:**
- Region: Slovenia/Croatia area (13.0-13.5°E, 45.5-46.0°N)
- Date: October 2023
- Max cloud cover: 25%
- Output: 2048x2048 true color JPEG

**Note:** Requires Copernicus credentials (not integrated with main backend yet)

---

### 7. `requirements.txt` - Python Dependencies

```
python-dotenv  # Load environment variables from .env
together       # Together AI Python SDK
flask          # Web framework
flask-cors     # CORS support for API
```

---

## 🔄 Data Flow Example

Let's trace a complete user interaction:

### Scenario: User asks "What's the burn severity in this area?"

**Step 1: Frontend (app.js)**
```javascript
// User clicks "Analyze with VLM"
handlePromptSubmission() {
    fetch('/api/analyze', {
        method: 'POST',
        body: JSON.stringify({
            prompt: "What's the burn severity in this area?",
            region: {north: 46.0, south: 45.5, ...},
            dateRange: {start: "2023-10-01", end: "2023-10-31"},
            layers: ["nbr", "ndvi"],
            conversationHistory: []
        })
    })
}
```

**Step 2: Backend (backend.py)**
```python
@app.route('/api/analyze', methods=['POST'])
def analyze_with_vlm():
    # 1. Extract data from request
    prompt = data.get('prompt')
    region = data.get('region')
    
    # 2. Find satellite image
    image_path = "satellite_data/sentinel2_20231007.jpg"
    
    # 3. Enhance prompt with context
    enhanced_prompt = f"""
    You are FireDoc VLM analyzing satellite imagery.
    
    User's Question: {prompt}
    
    Region: N{region['north']}°, S{region['south']}°...
    Date: 2023-10-01 to 2023-10-31
    
    Analyze burn severity focusing on NBR and NDVI indices.
    """
    
    # 4. Call AI
    response = analyze_image_with_vlm(image_path, enhanced_prompt)
    
    return jsonify({"success": True, "response": response})
```

**Step 3: Together AI API**
```python
def analyze_image_with_vlm(image_path, prompt):
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    
    # Create vision request
    stream = together_client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }}
            ]
        }],
        stream=True
    )
    
    # Stream response
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content
    
    return response
```

**Step 4: Frontend Displays Response**
```javascript
// Response arrives from backend
addAIMessage(data.response)
// Renders in chat interface with fire icon and styling
```

---

## 🎯 Key Design Decisions

### 1. Why Flask?
- **Lightweight:** Simple backend, doesn't need heavy framework
- **Python:** Same language as AI SDK and data processing
- **Easy static file serving:** Can serve HTML/CSS/JS directly

### 2. Why Streaming Response?
- **Better UX:** Users see response as it generates
- **Responsive:** Feels more interactive
- **Efficient:** Don't wait for full response before showing anything

### 3. Why Base64 Encoding?
- **API Requirement:** Together AI expects base64-encoded images
- **No URLs Needed:** Can send local files without hosting them
- **Simple:** Single request contains both prompt and image

### 4. Why Conversation History?
- **Context:** AI can reference previous questions
- **Follow-ups:** Natural conversation flow
- **Better Answers:** AI understands full context

---

## 🧪 Testing Guide

### Test 1: Vision API with Car Image
```bash
# Terminal
python together-main.py

# Or via API
curl http://localhost:5000/api/test-car-image
```
**Expected:** AI identifies car brand and model

### Test 2: Health Check
```bash
curl http://localhost:5000/api/health
```
**Expected:**
```json
{
  "status": "healthy",
  "together_api_configured": true,
  "images_available": 1
}
```

### Test 3: Full Workflow
1. Start backend: `python backend.py`
2. Open browser: `http://localhost:5000`
3. Draw rectangle on map
4. Click "Fetch Satellite Data"
5. Type prompt: "Describe this satellite image"
6. Click "Analyze with VLM"
7. See AI response in chat

---

## 🚀 Deployment Considerations

### For Production:

1. **Environment Variables:**
   - Never commit `.env` file
   - Use environment secrets in deployment platform

2. **Static Files:**
   - Consider CDN for CSS/JS
   - Compress images

3. **API Rate Limiting:**
   - Add rate limiting to prevent abuse
   - Cache common queries

4. **Error Handling:**
   - More robust error messages
   - Logging for debugging

5. **Security:**
   - HTTPS only
   - Input validation
   - Sanitize user prompts

---

## 📈 Future Enhancements

### Planned Features:

1. **Real-time Copernicus Integration**
   - Auto-fetch satellite data based on region selection
   - No manual image management

2. **Before/After Comparison**
   - Upload two images
   - AI compares burn progression

3. **Export Reports**
   - PDF generation of analysis
   - Include maps and AI insights

4. **User Authentication**
   - Save analysis history
   - Share reports with team

5. **Advanced Visualization**
   - Overlay burn severity on map
   - Heat maps for different indices

---

## 🎓 Learning Outcomes

### You'll Learn:

1. **Full-Stack Development:**
   - Frontend: HTML/CSS/JS
   - Backend: Python/Flask
   - API Integration

2. **Vision AI:**
   - How to use Vision-Language Models
   - Image encoding and transmission
   - Prompt engineering for vision tasks

3. **Geospatial Data:**
   - Working with satellite imagery
   - Coordinate systems
   - Map visualization

4. **Clean Code Principles:**
   - Clear function names
   - Comprehensive comments
   - Modular architecture

---

## 📞 Support & Resources

### Documentation:
- **Together AI:** https://docs.together.ai/
- **Flask:** https://flask.palletsprojects.com/
- **Leaflet:** https://leafletjs.com/
- **Copernicus:** https://dataspace.copernicus.eu/

### Troubleshooting:
Run `python check_setup.py` to diagnose issues

---

**Built with ❤️ for environmental monitoring and wildfire assessment**

