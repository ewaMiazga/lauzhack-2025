# 🔥 SATUK4 VLM

**Satellite AI for Terrain Understanding & Knowledge**

An intelligent Vision-Language Model platform that combines satellite imagery analysis with wildlife detection capabilities to provide comprehensive environmental monitoring and assessment.

## 🌍 Project Overview

**SATUK VLM** is a dual-purpose AI-powered environmental analysis platform designed for LauzHack 2025. It leverages state-of-the-art vision models to provide:

### 🛰️ **Satellite Analysis**
Analyze satellite imagery to assess wildfire burn severity, vegetation health, and environmental impact:
- Interactive map-based region selection
- Multi-temporal analysis with date range selection
- Support for multiple data layers (NBR, NDVI, SWIR, FIRMS)
- AI-powered burn severity assessment
- Vegetation recovery tracking
- Environmental impact analysis

### 🎥 **Wildlife Detection**
Advanced video analysis for wildlife monitoring and detection:
- Automatic animal detection and classification
- Species identification and counting
- Behavioral analysis
- Temporal activity pattern recognition
- Conservation-focused insights

## 🎯 Key Features

✅ **Interactive Map Interface** - Draw regions directly on the map  
✅ **AI Vision Analysis** - Powered by Together AI's Llama-Vision models  
✅ **Real-time Streaming** - AI responses stream in real-time  
✅ **Wildlife Video Analysis** - Detect and classify animals in camera trap footage  
✅ **Multi-layer Satellite Data** - NBR, NDVI, SWIR, and more  
✅ **Conversation History** - Follow-up questions with context  
✅ **Modern UI** - Clean, responsive design  

## 🛠️ Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (Vanilla)
- Leaflet.js for interactive maps
- Leaflet Draw for region selection
- Video.js for wildlife footage playback

**Backend:**
- Python 3.x
- Flask web framework with CORS support
- Together AI Vision API
  - `meta-llama/Llama-Vision-Free` for satellite analysis
  - `meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo` for wildlife detection
- Copernicus API for satellite data retrieval

**AI Models:**
- Vision-Language Models for image understanding
- Natural language processing for conversational interface
- Object detection and classification

## 🏗️ Project Structure

```
lauzhack-2025/
├── 🛰️ Satellite Analysis
│   ├── index.html              # Main satellite analysis interface
│   ├── app.js                  # Frontend JavaScript logic
│   ├── backend.py              # Flask API server (MAIN BACKEND)
│   ├── api-copernicus.py       # Copernicus satellite data fetcher
│   └── satellite_data/         # Downloaded satellite imagery
│       └── sentinel2_*.jpg     # Sentinel-2 satellite images
│
├── 🎥 Wildlife Detection
│   ├── wildlife-analysis.html  # Wildlife video analysis interface
│   ├── wildlife-analysis.js    # Wildlife frontend logic
│   ├── wildlife_backend.py     # Wildlife detection backend
│   └── videos/                 # Wildlife camera trap footage
│       └── *.mp4              # Video files for analysis
│
├── 🎨 Styling & Assets
│   ├── styles.css              # Global styling and layout
│   └── images/                 # Test images directory
│       └── car.jpg            # Sample image for API testing
│
├── 📋 Documentation
│   ├── README.md               # This file
│   ├── ARCHITECTURE.md         # System architecture documentation
│   ├── WILDLIFE_BACKEND_README.md   # Wildlife backend details
│   └── WILDLIFE_DEBUG.md       # Wildlife troubleshooting guide
│
├── 🔧 Configuration & Setup
│   ├── requirements.txt        # Python dependencies
│   ├── check_setup.py          # Setup verification script
│   ├── test_wildlife_setup.py  # Wildlife setup tester
│   └── .env                    # API keys (create this!)
│
└── 🚀 Demos & Tests
    └── together-main.py        # Together AI vision demo
```

## 🔄 How It Works

### System Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                                │
│                                                                  │
│  ┌─────────────────────┐      ┌─────────────────────┐         │
│  │  🛰️ Satellite UI    │      │  🎥 Wildlife UI      │         │
│  │  - Map Interface    │      │  - Video Player     │         │
│  │  - Region Selection │      │  - Detection View   │         │
│  │  - Chat Interface   │      │  - Chat Interface   │         │
│  └──────────┬──────────┘      └──────────┬──────────┘         │
│             │                             │                     │
└─────────────┼─────────────────────────────┼─────────────────────┘
              │                             │
              │ HTTP/JSON                   │ HTTP/JSON
              ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│   backend.py            │   │  wildlife_backend.py     │
│   (Satellite Analysis)  │   │  (Wildlife Detection)    │
│   Port: 5000            │   │  Port: 5001              │
└──────────┬──────────────┘   └──────────┬───────────────┘
           │                              │
           │ Together AI API              │ Together AI API
           │ (Llama-Vision-Free)          │ (Llama-90B-Vision)
           │                              │
           └──────────────┬───────────────┘
                          ▼
                  ┌────────────────┐
                  │  Together AI   │
                  │  Vision Models │
                  └────────────────┘
```

### Satellite Analysis Flow:

1. **User selects region** on the interactive map using drawing tools
2. **Configure date range** and data layers (NBR, NDVI, SWIR, FIRMS)
3. **Fetch satellite data** - Backend retrieves Sentinel-2 imagery
4. **Ask questions** about burn severity, vegetation health, impact
5. **AI analyzes imagery** using vision model with geographic context
6. **Receive detailed insights** streamed in real-time

### Wildlife Detection Flow:

1. **Upload video footage** or select from available camera trap videos
2. **AI analyzes frames** to detect animals and identify species
3. **Generate insights** about wildlife activity, behavior, patterns
4. **Interactive chat** to ask specific questions about detected wildlife
5. **Conservation insights** for ecological monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Together AI API key ([Get one here](https://api.together.xyz/))
- Modern web browser (Chrome, Firefox, Edge)

### Setup Instructions

#### 1. Clone the Repository
```bash
cd C:\projects\lauzhack-2025
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `flask` - Web framework
- `flask-cors` - Cross-origin support
- `together` - Together AI API client
- `python-dotenv` - Environment variable management
- `requests` - HTTP library

#### 3. Configure API Key

Create a `.env` file in the project root:

```env
TOGETHER_API_KEY=your_together_ai_api_key_here
```

🔑 **Get your API key:** https://api.together.xyz/

#### 4. Verify Setup

Run the automated setup checker:

```bash
python check_setup.py
```

This will verify:
- ✅ .env file exists
- ✅ API key is configured
- ✅ Required directories exist
- ✅ Python packages are installed
- ✅ Sample images are available

#### 5. Add Satellite Images (Optional)

Place satellite imagery in the `satellite_data/` directory:

```
satellite_data/
├── sentinel2_20251016_nbr.jpg
├── sentinel2_20251016_ndvi.jpg
└── ...
```

You can use `api-copernicus.py` to download real Sentinel-2 data from Copernicus.

#### 6. Add Wildlife Videos (Optional)

Place camera trap videos in the `videos/` directory for wildlife analysis.

### Running the Application

#### Start Satellite Analysis Backend:
```bash
python backend.py
```
Server will start on `http://localhost:5000`

#### Start Wildlife Detection Backend:
```bash
python wildlife_backend.py
```
Server will start on `http://localhost:5001`

#### Open in Browser:
- **Satellite Analysis:** http://localhost:5000
- **Wildlife Detection:** http://localhost:5000/wildlife-analysis.html

## 📖 User Guide

### 🛰️ Satellite Analysis

1. **Select a Region:**
   - Click the rectangle tool (⬜) on the map
   - Draw a box around your area of interest
   - See coordinates displayed in the sidebar

2. **Configure Settings:**
   - Set start and end dates for temporal analysis
   - Choose data layers:
     - **NBR** (Normalized Burn Ratio) - Burn severity
     - **NDVI** (Normalized Difference Vegetation Index) - Vegetation health
     - **SWIR** (Short-Wave Infrared) - Fire detection
     - **FIRMS** (Fire Information) - Active fires

3. **Fetch Data:**
   - Click "🚀 Fetch Satellite Data"
   - Wait for confirmation of available imagery

4. **Ask Questions:**
   - Type your question in the prompt box
   - Example prompts:
     - "Analyze the burn severity in this region"
     - "What's the vegetation recovery rate?"
     - "Estimate the total burned area in hectares"
     - "Compare the burn severity between different areas"
     - "Has vegetation started to recover?"
   - Click "✨ Analyze with VLM"

5. **Review Analysis:**
   - Read the AI's detailed assessment
   - Ask follow-up questions for deeper insights
   - Conversation history is maintained for context

### 🎥 Wildlife Detection

1. **Navigate to Wildlife Tab:**
   - Click "🎥 Wildlife Detection" in the navigation bar

2. **Select Video:**
   - Choose from available camera trap footage
   - Or specify a video file path

3. **Run Analysis:**
   - Click "Analyze Wildlife"
   - AI will process the video and detect animals

4. **Review Results:**
   - See detected species and counts
   - View activity patterns
   - Ask questions about animal behavior
   - Get conservation insights

## 📡 API Reference

### Satellite Analysis Backend (Port 5000)

#### `GET /api/health`
Check server health and configuration status.

**Response:**
```json
{
  "status": "healthy",
  "together_api_configured": true,
  "satellite_data_dir": "/path/to/satellite_data",
  "images_available": 5
}
```

#### `POST /api/fetch-data`
Retrieve satellite data for a specific region and date range.

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
    "start": "2025-10-01",
    "end": "2025-11-30"
  },
  "layers": ["nbr", "ndvi", "swir"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Found 3 satellite image(s)",
  "images": ["sentinel2_20251016_nbr.jpg", "..."]
}
```

#### `POST /api/analyze`
Analyze satellite imagery using Vision AI with conversational context.

**Request:**
```json
{
  "prompt": "What is the burn severity in this region?",
  "region": { "north": 46.0, "south": 45.5, "east": 13.5, "west": 13.0 },
  "dateRange": { "start": "2025-10-01", "end": "2025-11-30" },
  "layers": ["nbr", "ndvi"],
  "conversationHistory": [
    { "role": "user", "content": "Previous question..." },
    { "role": "assistant", "content": "Previous answer..." }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "Based on the NBR analysis of the satellite imagery...",
  "image_analyzed": "sentinel2_20251016_nbr.jpg"
}
```

#### `GET /api/test-car-image`
Test endpoint to verify Together AI vision API with sample image.

**Response:**
```json
{
  "success": true,
  "response": "The image shows a [detailed description]..."
}
```

### Wildlife Detection Backend (Port 5001)

#### `GET /api/health`
Check wildlife backend status.

#### `POST /api/analyze-video`
Analyze wildlife camera trap footage.

**Request:**
```json
{
  "video_path": "videos/Beaver camera trap footage.mp4",
  "prompt": "What animals are in this video?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Detected: 2 beavers, active during evening hours...",
  "species_detected": ["beaver"],
  "count": 2
}
```

## 🧪 Testing & Validation

### Test the Vision API

#### Option 1: Automated Setup Check
```bash
python check_setup.py
```
Validates your entire setup including API keys, directories, and dependencies.

#### Option 2: Test Car Image Recognition
```bash
curl http://localhost:5000/api/test-car-image
```
Tests the Together AI vision API with a sample car image.

#### Option 3: Standalone Vision Demo
```bash
python together-main.py
```
Runs a standalone demo that analyzes `images/car.jpg` and describes the vehicle.

#### Option 4: Wildlife Setup Check
```bash
python test_wildlife_setup.py
```
Validates wildlife detection backend configuration.

### Example Questions to Try

**Satellite Analysis:**
- "What is the burn severity classification in this region?"
- "Estimate the total area affected by fire"
- "Has vegetation started recovering since the fire?"
- "Compare the NDVI values before and after the burn"
- "What's the ecological impact of this wildfire?"

**Wildlife Detection:**
- "What animals are visible in this video?"
- "How many different species can you detect?"
- "What time of day were the animals most active?"
- "Describe the behavior of the detected animals"
- "Any signs of habitat degradation?"

## 💻 Code Architecture

### `backend.py` - Satellite Analysis Server

**Key Components:**

```python
# Core Functions
encode_image_to_base64(image_path)
# Converts satellite images to base64 for API transmission

analyze_image_with_vlm(image_path, prompt, conversation_history)
# Calls Together AI Vision API with SATUK system prompt

# API Endpoints
@app.route('/api/fetch-data', methods=['POST'])
# Handles satellite data retrieval requests

@app.route('/api/analyze', methods=['POST'])
# Processes AI analysis requests with geographic context
```

**System Prompt:**
```
You are SATUK VLM (Satellite AI for Terrain Understanding & Knowledge),
an expert AI assistant for analyzing satellite imagery to assess wildfire
burn severity and environmental impact.
```

### `wildlife_backend.py` - Wildlife Detection Server

**Key Components:**

```python
# Video Analysis
analyze_video_with_vlm(video_path, prompt)
# Processes wildlife video footage frame-by-frame

extract_video_frames(video_path, num_frames=10)
# Extracts representative frames for analysis

# API Endpoints
@app.route('/api/analyze-video', methods=['POST'])
# Handles wildlife video analysis requests
```

### `app.js` - Satellite Frontend Logic

**Key State Management:**

```javascript
const appState = {
    selectedRegion: null,      // Map coordinates
    dateRange: { start, end }, // Temporal range
    selectedLayers: [],        // Data layers
    conversationHistory: []    // Chat context
}

// Core Functions
initMap()                     // Leaflet map initialization
handlePromptSubmission()      // Send prompts to backend
updateChatInterface()         // Display AI responses
```

### `wildlife-analysis.js` - Wildlife Frontend Logic

**Key Components:**

```javascript
// Video handling
initVideoPlayer()             // Video.js initialization
analyzeCurrentFrame()         // Frame-by-frame analysis
displayDetectionResults()     // Show detected species
```

## 🌟 Current Features

### Satellite Analysis Module
✅ **Interactive Map Interface** - Leaflet-based region selection with drawing tools  
✅ **Multi-temporal Analysis** - Compare imagery across different dates  
✅ **Multiple Data Layers** - NBR, NDVI, SWIR, FIRMS support  
✅ **AI-Powered Assessment** - Automated burn severity analysis  
✅ **Geographic Context** - Coordinates and region info in analysis  
✅ **Conversation Memory** - Follow-up questions with context retention  

### Wildlife Detection Module
✅ **Video Analysis** - Process camera trap footage automatically  
✅ **Species Identification** - Detect and classify wildlife  
✅ **Activity Patterns** - Temporal behavior analysis  
✅ **Conservation Insights** - Ecological monitoring capabilities  

### Shared Features
✅ **Real-time Streaming** - AI responses stream as they're generated  
✅ **Modern UI** - Clean, responsive interface design  
✅ **Dual Backend** - Separate specialized servers for each module  
✅ **Error Handling** - Comprehensive error messages and recovery  
✅ **Setup Validation** - Automated configuration checking  

## 🚀 Future Enhancements

### Satellite Analysis Roadmap
- [ ] **Live Copernicus Integration** - Direct API fetching of satellite data
- [ ] **Multi-image Comparison** - Side-by-side before/after visualization
- [ ] **Custom Visualizations** - Render data layers directly on map
- [ ] **PDF Report Export** - Generate professional analysis reports
- [ ] **Time-series Analysis** - Track changes over extended periods
- [ ] **Batch Processing** - Analyze multiple regions simultaneously
- [ ] **Area Calculations** - Precise burn area measurements
- [ ] **Severity Heatmaps** - Visual severity classification overlays

### Wildlife Detection Roadmap
- [ ] **Real-time Detection** - Live camera feed analysis
- [ ] **Species Database** - Comprehensive wildlife reference library
- [ ] **Population Tracking** - Long-term monitoring and trends
- [ ] **Alert System** - Notifications for rare species detection
- [ ] **Habitat Analysis** - Environmental quality assessment
- [ ] **Multi-camera Support** - Network of camera traps
- [ ] **Behavior Classification** - Automated ethogram generation
- [ ] **Conservation Reports** - Automated biodiversity assessments

### Platform Enhancements
- [ ] **User Authentication** - Personal accounts and saved analyses
- [ ] **Data Persistence** - Database for historical analyses
- [ ] **API Rate Limiting** - Prevent abuse and manage costs
- [ ] **Mobile Support** - Responsive design for tablets/phones
- [ ] **Collaboration Tools** - Share analyses with team members
- [ ] **Integration APIs** - Connect with other environmental tools
- [ ] **Multi-language Support** - Internationalization
- [ ] **Dark Mode** - Alternative UI theme

## 🐛 Troubleshooting

### Common Issues & Solutions

**❌ API key not found**
```
Error: TOGETHER_API_KEY not configured
Solution: Create .env file with TOGETHER_API_KEY=your_key
```

**❌ No satellite images available**
```
Error: No images found in satellite_data/
Solution: Add JPEG/PNG satellite images to satellite_data/ directory
         or use api-copernicus.py to download Sentinel-2 data
```

**❌ CORS errors in browser**
```
Error: Access-Control-Allow-Origin header missing
Solution: Ensure flask-cors is installed: pip install flask-cors
         Verify backend.py is running on http://localhost:5000
```

**❌ Image analysis fails**
```
Error: Failed to analyze image
Solution: 
  1. Check that image file exists and is valid JPEG/PNG
  2. Verify image is not corrupted
  3. Check Together AI API key is valid
  4. Review backend.py logs for detailed error messages
```

**❌ Wildlife backend won't start**
```
Error: Port 5001 already in use
Solution: Kill process using port 5001 or change port in wildlife_backend.py
```

**❌ Video file not found**
```
Error: Video file does not exist
Solution: Place video files in videos/ directory
         Ensure file path is correct (case-sensitive on Linux)
```

**❌ Module import errors**
```
Error: ModuleNotFoundError: No module named 'flask'
Solution: Install all dependencies: pip install -r requirements.txt
```

### Getting Help

1. **Check setup:** Run `python check_setup.py`
2. **View logs:** Check terminal output from backend servers
3. **Verify API:** Test with `curl http://localhost:5000/api/health`
4. **Read docs:** See `ARCHITECTURE.md` and `WILDLIFE_BACKEND_README.md`

## 📚 Additional Documentation

- **`ARCHITECTURE.md`** - Detailed system architecture and diagrams
- **`WILDLIFE_BACKEND_README.md`** - Wildlife detection backend specifics
- **`WILDLIFE_DEBUG.md`** - Wildlife module troubleshooting guide
- **`report_prompt.txt`** - Template for wildfire analysis reports
- **`similar_wildfire_prompt.txt`** - Finding similar historical fires
- **`time_comparison_prompt.txt`** - Temporal comparison templates

## 🎓 Use Cases

### Environmental Monitoring
- Post-wildfire burn severity assessment
- Vegetation recovery tracking
- Ecological impact evaluation
- Wildlife habitat monitoring

### Conservation
- Biodiversity monitoring through camera traps
- Species population tracking
- Habitat quality assessment
- Protected area management

### Research
- Climate change impact studies
- Ecosystem resilience analysis
- Wildlife behavior research
- Long-term environmental trends

### Emergency Response
- Rapid wildfire damage assessment
- Resource allocation planning
- Recovery monitoring
- Impact documentation

## 🏆 LauzHack 2025

This project was created for **LauzHack 2025**, showcasing the power of Vision-Language Models for environmental monitoring and conservation.

**Team Focus:**
- Combining satellite imagery analysis with AI
- Wildlife detection and monitoring
- Real-world environmental applications
- User-friendly interfaces for non-technical users

## 📝 License

See `LICENSE` file for details.

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional satellite data sources
- More wildlife species detection
- Enhanced visualization tools
- Performance optimizations
- Documentation improvements

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

## 🙏 Acknowledgments

- **Together AI** - For providing excellent vision model APIs
- **Copernicus/ESA** - For Sentinel-2 satellite data
- **LauzHack 2025** - For the hackathon opportunity
- **Leaflet.js** - For the mapping framework
- **Open source community** - For amazing tools and libraries

## 📧 Contact

For questions or feedback about SATUK VLM, please open an issue in the repository.

---

**Built with ❤️ for environmental conservation and wildfire assessment**

🔥 **SATUK VLM** - *Satellite AI for Terrain Understanding & Knowledge*

