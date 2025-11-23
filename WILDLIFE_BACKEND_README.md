# Wildlife Detection Backend

This backend handles video analysis for wildlife detection using the Qwen VLM (Vision-Language Model).

## Features

- **Video Upload**: Accept video files (MP4, MOV, AVI, MKV, WEBM) up to 500MB
- **Frame Extraction**: Extract frames from videos using OpenCV
- **VLM Analysis**: Send frames to Qwen/Qwen2-VL-72B-Instruct for wildlife detection
- **Custom Prompts**: Support user-provided prompts for specific analysis needs
- **Video Persistence**: Keep video visible at the top during analysis results

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Make sure you have `opencv-python` installed for video frame extraction.

2. Set up your Together AI API key in `.env`:
```
TOGETHER_API_KEY=your_api_key_here
```

## Running the Backend

Start the wildlife backend server (runs on port 5001):
```bash
python wildlife_backend.py
```

The server will be available at `http://localhost:5001`

## API Endpoints

### `POST /api/upload-video`
Upload a video file for analysis.

**Form Data:**
- `video`: Video file
- `prompt`: (Optional) Custom prompt for analysis

**Response:**
```json
{
  "success": true,
  "video_id": "20250123_143022",
  "filename": "wildlife_video.mp4",
  "message": "Video uploaded successfully"
}
```

### `POST /api/analyze-video`
Analyze an uploaded video for wildlife detection.

**JSON Body:**
```json
{
  "video_id": "20250123_143022",
  "prompt": "Focus on identifying mammals",
  "sample_rate": 5
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "20250123_143022",
  "analysis": "Detailed VLM analysis text...",
  "video_metadata": {
    "fps": 30,
    "duration": 120.5,
    "width": 1920,
    "height": 1080
  },
  "frames_analyzed": 24
}
```

### `GET /api/test`
Test endpoint to verify the server is running.

## Configuration

- **Port**: 5001 (to avoid conflict with main backend on 5000)
- **Max Video Size**: 500MB
- **Frame Extraction Rate**: 1 frame per second
- **Frame Sampling Rate**: Analyzes every 5th frame by default (configurable)
- **VLM Model**: Qwen/Qwen2-VL-72B-Instruct

## How It Works

1. **Upload**: Video is uploaded and saved with a unique timestamp ID
2. **Frame Extraction**: OpenCV extracts frames at 1 FPS
3. **Sampling**: Every Nth frame is sampled to reduce API calls
4. **VLM Analysis**: Sampled frames are sent to Qwen VLM with user prompt
5. **Results**: VLM provides comprehensive wildlife detection analysis
6. **Cleanup**: Extracted frames are deleted after analysis

## Frontend Integration

The frontend (`wildlife-analysis.html`) automatically connects to this backend at `http://localhost:5001`. The video remains visible at the top of the results section during and after analysis.
