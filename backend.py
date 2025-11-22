"""
FireDoc VLM Backend Server
===========================
This Flask server connects the frontend map interface with:
1. Together AI Vision API - for analyzing satellite images
2. Copernicus satellite data - for fetching burn imagery

Simple, clean architecture:
- Frontend sends region coordinates and prompt
- Backend fetches satellite image for that region
- Vision AI analyzes the image and responds to the prompt
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from together import Together
from dotenv import load_dotenv
import os
import base64

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend

# Initialize Together AI client
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Configuration
SATELLITE_DATA_DIR = os.path.join(os.path.dirname(__file__), "satellite_data")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# Ensure directories exist
os.makedirs(SATELLITE_DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


def encode_image_to_base64(image_path):
    """
    Convert an image file to base64 encoding.

    Args:
        image_path: Path to the image file

    Returns:
        Base64 encoded string of the image
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image_with_vlm(image_path, prompt, conversation_history=None):
    """
    Analyze an image using Together AI Vision-Language Model.

    Args:
        image_path: Path to the image to analyze
        prompt: User's question about the image
        conversation_history: Previous conversation messages (optional)

    Returns:
        AI's response as a string
    """
    # Encode the image
    base64_image = encode_image_to_base64(image_path)

    # Build the messages list
    messages = []

    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)

    # Add the current user message with the image
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                },
            },
        ],
    })

    # Call Together AI Vision API
    stream = together_client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=messages,
        stream=True,
    )

    # Collect the streaming response
    response_text = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    return response_text


@app.route('/')
def serve_index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory('.', path)


@app.route('/satellite_data/<path:filename>')
def serve_satellite_image(filename: str):
    return send_from_directory(SATELLITE_DATA_DIR, filename)


@app.route('/api/fetch-data', methods=['POST'])
def fetch_satellite_data():
    """
    Fetch satellite data for the selected region and date range.

    Expected JSON payload:
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

    Returns:
        Success message with available images
    """
    print("\n" + "="*80)
    print("📡 [API] /api/fetch-data endpoint called")
    print("="*80)

    try:
        print(f"🔍 [DEBUG] Parsing request JSON...")
        data = request.json

        if data is None:
            print(f"❌ [ERROR] Request JSON is None!")
            return jsonify({
                "success": False,
                "message": "Invalid request: No JSON data received"
            }), 400

        print(f"✅ Request JSON parsed")

        region = data.get('region')
        date_range = data.get('dateRange')
        layers = data.get('layers', [])

        print(f"\n📊 Request details:")
        print(f"   Region: N:{region['north']}, S:{region['south']}, E:{region['east']}, W:{region['west']}")
        print(f"   Date Range: {date_range['start']} to {date_range['end']}")
        print(f"   Layers: {', '.join(layers)}")

        # For now, we'll use the existing satellite image in the satellite_data directory
        # In a full implementation, you would fetch from Copernicus API here
        print(f"\n🔍 [DEBUG] Scanning for satellite images...")
        print(f"   Directory: {SATELLITE_DATA_DIR}")

        if not os.path.exists(SATELLITE_DATA_DIR):
            print(f"⚠️ [WARNING] Directory doesn't exist, creating it...")
            os.makedirs(SATELLITE_DATA_DIR, exist_ok=True)

        all_files = os.listdir(SATELLITE_DATA_DIR)
        print(f"   Total files in directory: {len(all_files)}")

        images_meta = []
        for filename in all_files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(SATELLITE_DATA_DIR, filename)
                size_kb = os.path.getsize(file_path) / 1024
                url = f"/satellite_data/{filename}"
                print(f"   ✅ Found image: {filename} ({size_kb:.2f} KB)")
                images_meta.append({
                    "filename": filename,
                    "url": url,
                    "size_kb": round(size_kb, 2),
                    # We assume images correspond to the selected region for now
                    "bounds": {
                        "north": region['north'],
                        "south": region['south'],
                        "east": region['east'],
                        "west": region['west']
                    }
                })

        if not images_meta:
            print(f"\n❌ [ERROR] No satellite images found!")
            print("="*80 + "\n")
            return jsonify({
                "success": False,
                "message": "No satellite images available. Please add images to the satellite_data directory.",
                "images": []
            }), 404

        print(f"\n✅ [SUCCESS] Found {len(images_meta)} satellite image(s)")
        print("="*80 + "\n")

        return jsonify({
            "success": True,
            "message": f"Found {len(images_meta)} satellite image(s)",
            "images": images_meta
        })

    except Exception as e:
        print(f"\n❌❌❌ [CRITICAL ERROR] Exception in /api/fetch-data:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")

        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_with_vlm():
    """
    Analyze satellite imagery using Vision-Language Model.

    Expected JSON payload:
    {
        "prompt": "What is the burn severity in this region?",
        "region": {...},
        "dateRange": {...},
        "layers": [...],
        "conversationHistory": [...]
    }

    Returns:
        AI analysis response
    """
    print("\n" + "="*80)
    print("🤖 [API] /api/analyze endpoint called")
    print("="*80)

    try:
        # Step 1: Parse request data
        print(f"🔍 [DEBUG] Step 1: Parsing request data...")
        data = request.json

        if data is None:
            print(f"❌ [ERROR] Request JSON is None!")
            return jsonify({
                "success": False,
                "response": "Invalid request: No JSON data received"
            }), 400

        print(f"✅ Request JSON parsed successfully")
        print(f"   Keys in request: {list(data.keys())}")

        # Step 2: Extract fields
        print(f"\n🔍 [DEBUG] Step 2: Extracting fields from request...")
        prompt = data.get('prompt')
        region = data.get('region')
        date_range = data.get('dateRange')
        layers = data.get('layers', [])
        conversation_history = data.get('conversationHistory', [])

        print(f"   ✅ Prompt: {prompt[:100]}..." if prompt and len(prompt) > 100 else f"   ✅ Prompt: {prompt}")
        print(f"   ✅ Region: {region}")
        print(f"   ✅ Date range: {date_range}")
        print(f"   ✅ Layers: {layers}")
        print(f"   ✅ Conversation history length: {len(conversation_history)}")

        # Validate required fields
        if not prompt:
            print(f"❌ [ERROR] Prompt is missing or empty!")
            return jsonify({
                "success": False,
                "response": "Prompt is required"
            }, 400)

        if not region:
            print(f"❌ [ERROR] Region is missing!")
            return jsonify({
                "success": False,
                "response": "Region is required"
            }, 400)

        # Step 3: Find satellite images
        print(f"\n🔍 [DEBUG] Step 3: Looking for satellite images...")
        print(f"   Scanning directory: {SATELLITE_DATA_DIR}")

        if not os.path.exists(SATELLITE_DATA_DIR):
            print(f"❌ [ERROR] Satellite data directory does not exist!")
            os.makedirs(SATELLITE_DATA_DIR, exist_ok=True)
            print(f"   Created directory: {SATELLITE_DATA_DIR}")

        all_files = os.listdir(SATELLITE_DATA_DIR)
        print(f"   Found {len(all_files)} total files in directory")

        available_images = [f for f in all_files if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   Found {len(available_images)} image files: {available_images}")

        if not available_images:
            print(f"❌ [ERROR] No satellite images available!")
            return jsonify({
                "success": False,
                "response": "❌ No satellite images available for analysis. Please fetch data first."
            }), 404

        # Step 4: Select image
        print(f"\n🔍 [DEBUG] Step 4: Selecting image to analyze...")
        image_filename = available_images[0]
        image_path = os.path.join(SATELLITE_DATA_DIR, image_filename)
        print(f"   ✅ Selected image: {image_filename}")
        print(f"   Full path: {image_path}")

        # Step 5: Build enhanced prompt
        print(f"\n🔍 [DEBUG] Step 5: Building enhanced prompt...")
        enhanced_prompt = f"""You are FireDoc VLM, an expert AI assistant for analyzing satellite imagery to assess wildfire burn severity and environmental impact.

User's Question: {prompt}

Context:
- Image: Satellite imagery of the selected region
- Region Coordinates: North {region['north']}°, South {region['south']}°, East {region['east']}°, West {region['west']}°
- Date Range: {date_range['start']} to {date_range['end']}
- Data Layers: {', '.join(layers)}

Please analyze the image and provide a detailed, helpful response to the user's question. Focus on:
- Burn severity (if applicable)
- Vegetation health and recovery
- Environmental impact assessment
- Any visible patterns or anomalies

Be specific and use quantitative observations when possible."""

        print(f"   ✅ Enhanced prompt built ({len(enhanced_prompt)} characters)")

        # Step 6: Call AI analysis
        print(f"\n🔍 [DEBUG] Step 6: Calling AI analysis function...")
        ai_response = analyze_image_with_vlm(image_path, enhanced_prompt, conversation_history)

        if not ai_response:
            print(f"⚠️ [WARNING] AI returned empty response!")
            ai_response = "I analyzed the image but couldn't generate a response. Please try again."

        print(f"\n✅ [SUCCESS] Analysis complete!")
        print(f"   Response length: {len(ai_response)} characters")
        print(f"   First 100 chars: {ai_response[:100]}...")

        # Step 7: Return response
        print(f"\n🔍 [DEBUG] Step 7: Returning JSON response...")
        response_data = {
            "success": True,
            "response": ai_response,
            "image_analyzed": image_filename
        }
        print(f"   ✅ Response prepared, sending to client...")
        print("="*80 + "\n")

        return jsonify(response_data)

    except Exception as e:
        print(f"\n❌❌❌ [CRITICAL ERROR] Exception in /api/analyze endpoint:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")

        return jsonify({
            "success": False,
            "response": f"Sorry, I encountered an error: {type(e).__name__} - {str(e)}"
        }), 500


@app.route('/api/test-car-image', methods=['GET'])
def test_car_image():
    """
    Test endpoint to analyze the car.jpg image.
    This demonstrates the vision API working with a simple image.
    """
    try:
        car_image_path = os.path.join(IMAGES_DIR, "car.jpg")

        if not os.path.exists(car_image_path):
            return jsonify({
                "success": False,
                "message": "car.jpg not found in images directory"
            }), 404

        print("\n🚗 Testing car image analysis...")

        # Analyze the car image
        response = analyze_image_with_vlm(
            car_image_path,
            "What car brand is it? Please identify the make and model if possible."
        )

        print(f"   ✅ Car analysis complete!")

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the server and API are working."""
    try:
        api_key = os.getenv("TOGETHER_API_KEY")
        return jsonify({
            "status": "healthy",
            "together_api_configured": bool(api_key),
            "satellite_data_dir": SATELLITE_DATA_DIR,
            "images_available": len([f for f in os.listdir(SATELLITE_DATA_DIR)
                                    if f.endswith(('.jpg', '.jpeg', '.png'))])
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 FireDoc VLM Backend Server")
    print("="*60)
    print(f"📁 Satellite Data Directory: {SATELLITE_DATA_DIR}")
    print(f"📁 Images Directory: {IMAGES_DIR}")

    # Check API key
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        print("✅ Together AI API key configured")
    else:
        print("⚠️  Warning: TOGETHER_API_KEY not found in .env file")

    print("\n🚀 Starting server on http://localhost:5000")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
