# 🚀 Quick Start Guide - FireDoc VLM

## ⚡ Get Running in 3 Steps

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd C:\projects\lauzhack-2025
python backend.py
```

You should see:
```
============================================================
🔥 FireDoc VLM Backend Server
============================================================
📁 Satellite Data Directory: C:\projects\lauzhack-2025\satellite_data
📁 Images Directory: C:\projects\lauzhack-2025\images
✅ Together AI API key configured

🚀 Starting server on http://localhost:5000
============================================================
```

### Step 2: Open Your Browser

Navigate to:
```
http://localhost:5000
```

### Step 3: Start Analyzing!

1. **Select a Region**
   - Click the rectangle tool on the map (📐 icon in top-left)
   - Draw a box on the map
   - See coordinates appear in the sidebar

2. **Fetch Data**
   - Click "🚀 Fetch Satellite Data"
   - Wait for success message

3. **Ask Questions**
   - Type in the prompt box, for example:
     - "Describe what you see in this satellite image"
     - "What is the vegetation health in this area?"
     - "Are there any signs of fire damage?"
   - Click "✨ Analyze with VLM"
   - Watch AI analyze the image!

---

## 🧪 Quick Tests

### Test 1: Health Check
```bash
# Open new terminal
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "together_api_configured": true,
  "satellite_data_dir": "C:\\projects\\lauzhack-2025\\satellite_data",
  "images_available": 1
}
```

### Test 2: Car Image Analysis
```bash
curl http://localhost:5000/api/test-car-image
```

Expected: JSON response with AI describing the car brand

### Test 3: Standalone Vision Script
```bash
python together-main.py
```

Expected: Streaming response about car brand

---

## 📊 Understanding the Flow

```
1. User draws rectangle on map
   ↓
2. Frontend captures coordinates
   ↓
3. User clicks "Fetch Data"
   ↓
4. Backend checks satellite_data/ directory
   ↓
5. User types question
   ↓
6. Frontend sends to /api/analyze
   ↓
7. Backend loads satellite image
   ↓
8. Backend encodes image to base64
   ↓
9. Backend calls Together AI Vision API
   ↓
10. AI analyzes image and responds
   ↓
11. Response streams back to frontend
   ↓
12. User sees analysis in chat interface
```

---

## 🎯 Example Prompts to Try

### For Burn Assessment:
- "Analyze the burn severity in this satellite image"
- "What percentage of this area shows signs of fire damage?"
- "Compare the vegetation health across this region"

### For General Analysis:
- "Describe the land use patterns in this image"
- "What natural features are visible?"
- "Are there any bodies of water in this area?"

### For Technical Details:
- "What is the NDVI (vegetation index) like in this region?"
- "Analyze the spectral signature of the burned areas"
- "Compare the pre and post-fire conditions"

---

## 🛠️ Troubleshooting

### Problem: Server won't start
**Solution:**
1. Check if port 5000 is already in use
2. Run: `python check_setup.py` to verify configuration
3. Make sure .env file exists with TOGETHER_API_KEY

### Problem: No satellite images available
**Solution:**
1. Verify `satellite_data/` directory exists
2. Add JPEG or PNG images to that directory
3. Check file permissions

### Problem: AI analysis fails
**Solution:**
1. Verify API key in .env file
2. Check internet connection
3. Ensure image file exists and is valid

### Problem: CORS errors in browser
**Solution:**
1. Make sure flask-cors is installed: `pip install flask-cors`
2. Restart the backend server
3. Clear browser cache

---

## 📱 Browser Compatibility

✅ Chrome 90+
✅ Firefox 88+
✅ Edge 90+
✅ Safari 14+

---

## 🔐 Security Notes

### For Development:
- ✅ TOGETHER_API_KEY stored in .env (git-ignored)
- ✅ CORS enabled for localhost only
- ✅ No sensitive data in frontend

### For Production:
- 🔒 Use HTTPS
- 🔒 Add rate limiting
- 🔒 Validate all user inputs
- 🔒 Set up proper CORS policies
- 🔒 Use environment secrets platform

---

## 📚 Additional Resources

### Learn More:
- **Flask Tutorial:** https://flask.palletsprojects.com/tutorial/
- **Together AI Docs:** https://docs.together.ai/
- **Leaflet.js Guide:** https://leafletjs.com/examples.html
- **Satellite Data:** https://dataspace.copernicus.eu/

### Files to Read:
- `README.md` - Full project documentation
- `PROJECT_SUMMARY.md` - Detailed technical explanation
- `backend.py` - Well-commented backend code
- `app.js` - Frontend logic with explanations

---

## 🎉 You're All Set!

Your FireDoc VLM system is now running and ready to analyze satellite imagery!

**Next Steps:**
1. Explore the map interface
2. Try different regions
3. Ask various questions
4. Learn from the AI responses
5. Customize prompts for your use case

**Happy analyzing! 🔥🛰️🤖**

