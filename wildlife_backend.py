"""
Wildlife Detection Backend Server
==================================
This Flask server handles video uploads and VLM analysis for wildlife detection.

Features:
- Accept video uploads from frontend
- Extract frames from video
- Send frames to Qwen VLM for analysis
- Process custom user prompts
- Return wildlife detection results
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from together import Together
from dotenv import load_dotenv
import os
import base64
import cv2
import shutil
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend

# Initialize Together AI client
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_videos")
FRAMES_DIR = os.path.join(os.path.dirname(__file__), "video_frames")
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image_to_base64(image_path):
    """
    Convert an image file to base64 encoding.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_video_frames(video_path, output_dir, fps=1):
    """
    Extract frames from video at specified frame rate.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        fps: Frames per second to extract (default: 1 frame per second)
        
    Returns:
        List of frame file paths and video metadata
    """
    print(f"[EXTRACT] Opening video file: {video_path}")
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print(f"[ERROR] Could not open video file: {video_path}")
        raise Exception("Could not open video file")
    
    print("[EXTRACT] Video opened successfully")
    
    # Get video properties
    video_fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Calculate frame interval
    frame_interval = int(video_fps / fps) if video_fps > fps else 1
    
    frame_paths = []
    frame_count = 0
    saved_count = 0
    
    print(f"[EXTRACT] Starting frame extraction (interval: {frame_interval} frames)")
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        # Save frame at specified interval
        if frame_count % frame_interval == 0:
            frame_filename = f"frame_{saved_count:04d}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            saved_count += 1
            if saved_count % 10 == 0:
                print(f"[EXTRACT] Extracted {saved_count} frames...")
        
        frame_count += 1
    
    video.release()
    print(f"[EXTRACT] Completed: {len(frame_paths)} frames extracted from {frame_count} total frames")
    
    metadata = {
        'fps': video_fps,
        'total_frames': total_frames,
        'duration': duration,
        'width': width,
        'height': height,
        'extracted_frames': len(frame_paths)
    }
    
    return frame_paths, metadata


def analyze_frames_with_vlm(frame_paths, user_prompt="", sample_rate=5):
    """
    Analyze video frames using Qwen VLM.
    
    Args:
        frame_paths: List of paths to frame images
        user_prompt: Custom user prompt for analysis
        sample_rate: Analyze every Nth frame to reduce API calls
        
    Returns:
        Analysis results from the VLM
    """
    # Sample frames to reduce processing time and cost
    sampled_frames = frame_paths[::sample_rate] if len(frame_paths) > sample_rate else frame_paths
    print(f"[VLM] Analyzing {len(sampled_frames)} frames (sampled from {len(frame_paths)} total)")
    
    # Default prompt if none provided
    if not user_prompt:
        user_prompt = """Analyze this video for wildlife detection. For each frame:
1. Identify all animals visible
2. Note their species if recognizable
3. Describe their behavior
4. Estimate time of appearance
5. Note any notable patterns or behaviors

Provide a comprehensive summary of all wildlife observed."""
    
    print(f"[VLM] Using prompt: {user_prompt[:100]}...")
    
    # Prepare message content with all sampled frames
    message_content = [{"type": "text", "text": user_prompt}]
    
    # Add frames as images
    print(f"[VLM] Encoding {len(sampled_frames)} frames to base64...")
    for i, frame_path in enumerate(sampled_frames):
        try:
            base64_image = encode_image_to_base64(frame_path)
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
            if (i + 1) % 5 == 0:
                print(f"[VLM] Encoded {i + 1}/{len(sampled_frames)} frames")
        except Exception as e:
            print(f"[ERROR] Error encoding frame {frame_path}: {e}")
    
    # Call Together AI with Qwen VLM
    print("[VLM] Sending request to Qwen/Qwen2.5-VL-72B-Instruct...")
    try:
        response = together_client.chat.completions.create(
            model="Qwen/Qwen2.5-VL-72B-Instruct",
            messages=[{
                "role": "user",
                "content": message_content
            }],
            max_tokens=4096,
            temperature=0.7,
        )
        
        print(f"[VLM] Received response from VLM (length: {len(response.choices[0].message.content)} chars)")
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] Error calling VLM API: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception details: {str(e)}")
        raise


@app.route('/')
def index():
    """Serve the wildlife analysis page."""
    return send_from_directory('.', 'wildlife-analysis.html')


@app.route('/wildlife-analysis.html')
def wildlife_page():
    """Serve the wildlife analysis page."""
    return send_from_directory('.', 'wildlife-analysis.html')


@app.route('/wildlife-analysis.js')
def wildlife_js():
    """Serve the wildlife analysis JavaScript."""
    return send_from_directory('.', 'wildlife-analysis.js')


@app.route('/styles.css')
def styles():
    """Serve the CSS file."""
    return send_from_directory('.', 'styles.css')


@app.route('/api/upload-video', methods=['POST'])
def upload_video():
    """
    Handle video upload from frontend.
    
    Expected form data:
        - video: Video file
        - prompt: Optional custom prompt for analysis
    
    Returns:
        JSON with upload status and video ID
    """
    print("[UPLOAD] Received video upload request")
    # Check if video file is present
    if 'video' not in request.files:
        print("[ERROR] No video file in request")
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    print(f"[UPLOAD] File name: {video_file.filename}")
    
    if video_file.filename == '':
        print("[ERROR] Empty filename")
        return jsonify({'error': 'No video file selected'}), 400
    
    if not allowed_file(video_file.filename):
        print(f"[ERROR] Invalid file type: {video_file.filename}")
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Generate unique video ID
    video_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    print(f"[UPLOAD] Generated video ID: {video_id}")
    
    # Save video file
    video_filename = f"{video_id}_{video_file.filename}"
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    print(f"[UPLOAD] Saving to: {video_path}")
    video_file.save(video_path)
    
    # Check file size
    file_size = os.path.getsize(video_path)
    print(f"[UPLOAD] File size: {file_size / (1024*1024):.2f} MB")
    if file_size > MAX_VIDEO_SIZE:
        print("[ERROR] File exceeds size limit")
        os.remove(video_path)
        return jsonify({'error': 'Video file exceeds 500MB limit'}), 400
    
    print(f"[UPLOAD] Video uploaded successfully: {video_id}")
    return jsonify({
        'success': True,
        'video_id': video_id,
        'filename': video_file.filename,
        'message': 'Video uploaded successfully'
    }), 200


@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    """
    Analyze uploaded video for wildlife detection.
    
    Expected JSON:
        - video_id: ID of uploaded video
        - prompt: Custom user prompt (optional)
        - sample_rate: Frame sampling rate (optional, default: 5)
    
    Returns:
        JSON with wildlife detection results
    """
    print("\n[ANALYZE] Received analysis request")
    data = request.json
    print(f"[ANALYZE] Request data: {data}")
    
    if not data or 'video_id' not in data:
        print("[ERROR] No video_id in request")
        return jsonify({'error': 'No video_id provided'}), 400
    
    video_id = data['video_id']
    user_prompt = data.get('prompt', '')
    sample_rate = data.get('sample_rate', 5)
    print(f"[ANALYZE] Video ID: {video_id}")
    print(f"[ANALYZE] Custom prompt: {'Yes' if user_prompt else 'No (using default)'}")
    print(f"[ANALYZE] Sample rate: {sample_rate}")
    
    # Find video file
    print(f"[ANALYZE] Looking for video in: {UPLOAD_DIR}")
    video_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(video_id)]
    print(f"[ANALYZE] Found video files: {video_files}")
    
    if not video_files:
        print(f"[ERROR] Video not found for ID: {video_id}")
        return jsonify({'error': 'Video not found'}), 404
    
    video_path = os.path.join(UPLOAD_DIR, video_files[0])
    print(f"[ANALYZE] Video path: {video_path}")
    
    # Create directory for this video's frames
    frames_output_dir = os.path.join(FRAMES_DIR, video_id)
    os.makedirs(frames_output_dir, exist_ok=True)
    print(f"[ANALYZE] Frames output directory: {frames_output_dir}")
    
    try:
        # Extract frames from video
        print(f"[ANALYZE] Starting frame extraction for video {video_id}")
        frame_paths, video_metadata = extract_video_frames(video_path, frames_output_dir, fps=1)
        
        if not frame_paths:
            print("[ERROR] No frames extracted from video")
            return jsonify({'error': 'No frames could be extracted from video'}), 500
        
        print(f"[ANALYZE] Successfully extracted {len(frame_paths)} frames")
        print(f"[ANALYZE] Video metadata: {video_metadata}")
        
        # Analyze frames with VLM
        print("[ANALYZE] Starting VLM analysis...")
        analysis_result = analyze_frames_with_vlm(frame_paths, user_prompt, sample_rate)
        
        print("[ANALYZE] VLM analysis complete!")
        
        # Clean up frames after analysis
        print(f"[ANALYZE] Cleaning up frames from {frames_output_dir}")
        shutil.rmtree(frames_output_dir)
        
        result = {
            'success': True,
            'video_id': video_id,
            'analysis': analysis_result,
            'video_metadata': video_metadata,
            'frames_analyzed': len(frame_paths[::sample_rate])
        }
        print(f"[ANALYZE] Returning result (analysis length: {len(analysis_result)} chars)")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] Error analyzing video: {e}")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        # Clean up on error
        if os.path.exists(frames_output_dir):
            shutil.rmtree(frames_output_dir)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify server is running."""
    return jsonify({
        'status': 'ok',
        'message': 'Wildlife detection backend is running',
        'model': 'Qwen/Qwen2-VL-72B-Instruct'
    }), 200


if __name__ == '__main__':
    print("=" * 50)
    print("Wildlife Detection Backend Server")
    print("=" * 50)
    print("Using VLM: Qwen/Qwen2-VL-72B-Instruct")
    print("Server starting on http://localhost:5001")
    print("=" * 50)
    
    app.run(debug=True, port=5001, host='0.0.0.0')
