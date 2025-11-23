# Wildlife Backend Debugging Guide

## What Was Added

### Comprehensive Logging
Added detailed logging throughout the entire video analysis pipeline to help identify where errors occur:

**Backend Logging (`wildlife_backend.py`):**
- `[UPLOAD]` - Video upload process
- `[ANALYZE]` - Analysis request handling
- `[EXTRACT]` - Frame extraction from video
- `[VLM]` - Vision-Language Model API calls
- `[ERROR]` - Error conditions with full traceback

**Frontend Logging (`wildlife-analysis.js`):**
- `[FRONTEND]` - All client-side operations
- Detailed error messages with response status codes
- Console logging at each step of the upload/analysis process

### Bug Fixes

1. **Model Name Corrected**: Changed from `Qwen/Qwen2-VL-72B-Instruct` to `Qwen/Qwen2.5-VL-72B-Instruct` (correct model name)

2. **Better Error Handling**: 
   - Full exception tracebacks in logs
   - Detailed error responses to frontend
   - User-friendly error messages with instructions

3. **Progress Tracking**:
   - Frame extraction progress (every 10 frames)
   - Frame encoding progress (every 5 frames)
   - Request/response logging

## How to Debug

### 1. Run the Test Script
```bash
python test_wildlife_setup.py
```
This checks:
- Python dependencies (opencv-python, together, flask, flask-cors)
- Together API key
- Directory structure

### 2. Start the Backend with Logging
```bash
python wildlife_backend.py
```
You'll see detailed logs like:
```
[UPLOAD] Received video upload request
[UPLOAD] File name: wildlife_video.mp4
[UPLOAD] File size: 15.23 MB
[UPLOAD] Video uploaded successfully: 20250123_143022
```

### 3. Monitor Browser Console
Open browser DevTools (F12) and watch the Console tab for:
```
[FRONTEND] Starting video upload...
[FRONTEND] Video file: wildlife_video.mp4 15234567 bytes
[FRONTEND] Upload response status: 200
```

### 4. Common Issues and Solutions

**Issue: "Failed to upload video"**
- Check: Is backend running on port 5001?
- Check: CORS enabled?
- Look for: `[UPLOAD]` logs in backend terminal

**Issue: "Failed to analyze video"**
- Check: OpenCV installed? (`pip install opencv-python`)
- Check: Together API key set in .env?
- Look for: `[EXTRACT]` and `[VLM]` logs in backend

**Issue: "Could not open video file"**
- Check: Video format supported (mp4, mov, avi, mkv, webm)?
- Check: File not corrupted?
- Look for: `[ERROR] Could not open video file` in logs

**Issue: VLM API errors**
- Check: API key valid?
- Check: Model name correct (Qwen2.5-VL)?
- Look for: `[ERROR] Error calling VLM API` with details

### 5. Reading the Logs

**Successful Flow:**
```
[UPLOAD] Received video upload request
[UPLOAD] File name: video.mp4
[UPLOAD] File size: 10.50 MB
[UPLOAD] Video uploaded successfully: 20250123_143022

[ANALYZE] Received analysis request
[ANALYZE] Video ID: 20250123_143022
[ANALYZE] Looking for video in: /path/to/uploaded_videos
[ANALYZE] Found video files: ['20250123_143022_video.mp4']
[ANALYZE] Starting frame extraction

[EXTRACT] Opening video file: /path/to/video.mp4
[EXTRACT] Video opened successfully
[EXTRACT] Starting frame extraction (interval: 30 frames)
[EXTRACT] Extracted 10 frames...
[EXTRACT] Completed: 24 frames extracted from 720 total frames

[VLM] Analyzing 5 frames (sampled from 24 total)
[VLM] Encoding 5 frames to base64...
[VLM] Encoded 5/5 frames
[VLM] Sending request to Qwen/Qwen2.5-VL-72B-Instruct...
[VLM] Received response from VLM (length: 1234 chars)

[ANALYZE] VLM analysis complete!
[ANALYZE] Returning result (analysis length: 1234 chars)
```

**Error Flow:**
```
[UPLOAD] Received video upload request
[ERROR] Invalid file type: video.avi

OR

[EXTRACT] Opening video file: /path/to/video.mp4
[ERROR] Could not open video file: /path/to/video.mp4

OR

[VLM] Sending request to Qwen/Qwen2.5-VL-72B-Instruct...
[ERROR] Error calling VLM API: API key invalid
[ERROR] Exception type: AuthenticationError
[ERROR] Traceback: ...
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install opencv-python
   ```

2. **Check setup:**
   ```bash
   python test_wildlife_setup.py
   ```

3. **Start backend:**
   ```bash
   python wildlife_backend.py
   ```

4. **Open frontend:**
   - Navigate to `http://localhost:5001/wildlife-analysis.html`
   - Upload a video
   - Watch logs in both terminal and browser console

5. **Debug issues:**
   - Look for `[ERROR]` in backend logs
   - Check browser console for `[FRONTEND]` errors
   - Verify all prerequisites are met

## What to Report

If you encounter an error, please provide:
1. The last 20-30 lines from the backend terminal
2. The browser console output
3. Video file format and size
4. Any error messages displayed to user
