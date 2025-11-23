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
import requests
import hashlib

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


def analyze_image_with_vlm(image_paths, prompt, conversation_history=None):
    """
    Analyze one or more images using Together AI Vision-Language Model.

    Args:
        image_paths: Single path (string) or list of paths to images (for before/after)
        prompt: User's question about the image(s)
        conversation_history: Previous conversation messages (optional)

    Returns:
        AI's response as a string
    """
    # Handle both single image and list of images
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    
    # Build the messages list
    messages = []

    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)

    # Build content array with text and images
    content = [{"type": "text", "text": prompt}]
    
    # Add all images to the content
    for image_path in image_paths:
        base64_image = encode_image_to_base64(image_path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            },
        })
    
    # Add the current user message with all images
    messages.append({
        "role": "user",
        "content": content,
    })

    # Call Together AI Vision API
    stream = together_client.chat.completions.create(
        model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
        messages=messages,
        stream=True,
    )

    # Collect the streaming response
    response_text = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    return response_text


def get_copernicus_token():
    """Obtain an access token from Copernicus Data Space. Returns token string or raises Exception."""
    if not COPERNICUS_USERNAME or not COPERNICUS_PASSWORD:
        raise RuntimeError("COPERNICUS_USERNAME or COPERNICUS_PASSWORD missing in environment (.env)")
    token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    resp = requests.post(token_url, data={
        "grant_type": "password",
        "username": COPERNICUS_USERNAME,
        "password": COPERNICUS_PASSWORD,
        "client_id": "cdse-public"
    }, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Token request failed ({resp.status_code}): {resp.text[:250]}")
    return resp.json().get("access_token")


def query_sentinel_products_with_pagination(region: dict, date_range: dict, token: str, max_cloud: int = 35):
    """
    Query Copernicus OData API for all Sentinel-2 products matching criteria.
    Handles pagination automatically to retrieve all results.
    
    Returns list of product metadata dictionaries.
    """
    from urllib.parse import quote
    
    minLon = region['west']
    minLat = region['south']
    maxLon = region['east']
    maxLat = region['north']
    
    # Build WKT polygon for area of interest
    wkt_polygon = (
        f"POLYGON(("
        f"{minLon} {minLat},"
        f"{maxLon} {minLat},"
        f"{maxLon} {maxLat},"
        f"{minLon} {maxLat},"
        f"{minLon} {minLat}"
        f"))"
    )
    
    # Build OData filter
    filters = [
        "Collection/Name eq 'SENTINEL-2'",
        "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A')",
        f"OData.CSC.Intersects(area=geography'SRID=4326;{wkt_polygon}')",
        f"ContentDate/Start gt {date_range['start']}T00:00:00.000Z",
        f"ContentDate/Start lt {date_range['end']}T23:59:59.999Z",
        f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le {max_cloud})"
    ]
    
    filter_string = " and ".join(filters)
    base_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    query_url = f"{base_url}?$filter={quote(filter_string)}&$orderby=ContentDate/Start desc&$top=1000"
    
    all_products = []
    current_url = query_url
    page_num = 1
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"📡 Querying Copernicus OData API for products...")
    
    while current_url:
        print(f"   📄 Fetching page {page_num}...")
        
        try:
            resp = requests.get(current_url, headers=headers, timeout=60)
            
            if resp.status_code != 200:
                print(f"   ❌ Query failed ({resp.status_code}): {resp.text[:300]}")
                break
            
            data = resp.json()
            products = data.get('value', [])
            all_products.extend(products)
            
            print(f"   ✅ Retrieved {len(products)} products from page {page_num}")
            print(f"   📊 Total products so far: {len(all_products)}")
            
            # Check for next page
            next_link = data.get('@odata.nextLink')
            if next_link:
                print(f"   🔗 More pages available, continuing...")
                current_url = next_link
                page_num += 1
            else:
                print(f"   ✅ All pages retrieved!")
                current_url = None
                
        except Exception as e:
            print(f"   ❌ Error on page {page_num}: {str(e)}")
            break
    
    print(f"📦 Total products found: {len(all_products)}")
    return all_products


def get_evalscript_for_layer(layer: str) -> str:
    """
    Generate the correct evalscript based on the selected layer.

    Args:
        layer: Layer type ('truecolor', 'ndvi', 'nbr', etc.)

    Returns:
        Evalscript string for Sentinel Hub API
    """
    if layer == 'ndvi':
        # NDVI (Normalized Difference Vegetation Index)
        # Measures vegetation health: -1 to +1
        # Green = healthy vegetation, Red/Brown = bare soil/dead vegetation
        return """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "SCL"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  // Calculate NDVI: (NIR - Red) / (NIR + Red)
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  
  // Color visualization
  if (ndvi < 0) {
    // Water or clouds (blue)
    return [0.2, 0.2, 1.0];
  } else if (ndvi < 0.2) {
    // Bare soil, burned areas (brown/red)
    return [0.8, 0.4, 0.2];
  } else if (ndvi < 0.4) {
    // Sparse vegetation (yellow/light green)
    return [0.9, 0.9, 0.3];
  } else if (ndvi < 0.6) {
    // Moderate vegetation (green)
    return [0.3, 0.8, 0.3];
  } else {
    // Dense vegetation (dark green)
    return [0.0, 0.5, 0.0];
  }
}
"""

    elif layer == 'nbr':
        # NBR (Normalized Burn Ratio)
        # Used to detect burned areas
        return """
//VERSION=3
function setup() {
  return {
    input: ["B08", "B12"],
    output: { bands: 3 }
  };
}

function evaluatePixel(sample) {
  // Calculate NBR: (NIR - SWIR) / (NIR + SWIR)
  let nbr = (sample.B08 - sample.B12) / (sample.B08 + sample.B12);
  
  // Color visualization for burn severity
  if (nbr < -0.25) {
    // High severity burn (dark red)
    return [0.5, 0.0, 0.0];
  } else if (nbr < -0.1) {
    // Moderate-high severity (red)
    return [0.9, 0.2, 0.0];
  } else if (nbr < 0.1) {
    // Moderate-low severity (orange)
    return [1.0, 0.6, 0.0];
  } else if (nbr < 0.3) {
    // Low severity / unburned (yellow)
    return [1.0, 1.0, 0.3];
  } else {
    // Healthy vegetation (green)
    return [0.0, 0.7, 0.0];
  }
}
"""

    else:  # 'truecolor' or default
        # True color RGB
        return """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B03", "B02"],
    output: { bands: 3 }
  };
}
function evaluatePixel(sample) {
  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
}
"""


def download_satellite_image_for_product(product: dict, region: dict, token: str, layer: str = 'truecolor', max_cloud: int = 35):
    """
    Download a Sentinel-2 image for a specific product and layer.

    Args:
        product: Product metadata from Copernicus
        region: Geographic bounds
        token: Copernicus API token
        layer: Layer type ('truecolor', 'ndvi', 'nbr')
        max_cloud: Maximum cloud coverage percentage

    Returns:
        dict with metadata or raises Exception on failure
    """
    # Extract product information
    product_name = product.get('Name', 'unknown')
    sensing_start = product.get('ContentDate', {}).get('Start', '')

    if not sensing_start:
        raise ValueError(f"No sensing date for product {product_name}")

    # Parse sensing date
    sensing_date = sensing_start.split('T')[0]

    # Get the appropriate evalscript for the selected layer
    evalscript = get_evalscript_for_layer(layer)

    minLon = region['west']
    minLat = region['south']
    maxLon = region['east']
    maxLat = region['north']
    
    # Dynamic sizing
    width = 1024
    lat_span = maxLat - minLat
    lon_span = maxLon - minLon
    height = int(max(256, min(2048, (lat_span / max(lon_span, 1e-6)) * width)))
    
    process_url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    payload = {
        "input": {
            "bounds": {"bbox": [minLon, minLat, maxLon, maxLat]},
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{sensing_date}T00:00:00Z",
                        "to": f"{sensing_date}T23:59:59Z"
                    },
                    "maxCloudCoverage": max_cloud
                }
            }]
        },
        "output": {
            "width": width,
            "height": height,
            "responses": [{
                "identifier": "default",
                "format": {"type": "image/jpeg"}
            }]
        },
        "evalscript": evalscript
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "image/jpeg"
    }
    
    resp = requests.post(process_url, json=payload, headers=headers, timeout=120)
    
    if resp.status_code != 200:
        raise RuntimeError(f"Processing API failed ({resp.status_code}): {resp.text[:300]}")
    
    content = resp.content
    hash_part = hashlib.sha256(content[:2000]).hexdigest()[:8]
    # Include layer name in filename to avoid overwrites
    filename = f"sentinel2_{sensing_date.replace('-', '')}_{layer}_{hash_part}.jpg"
    save_path = os.path.join(SATELLITE_DATA_DIR, filename)
    
    with open(save_path, 'wb') as f:
        f.write(content)
    
    size_kb = round(len(content) / 1024, 2)
    
    return {
        "filename": filename,
        "path": save_path,
        "size_kb": size_kb,
        "url": f"/satellite_data/{filename}",
        "sensing_date": sensing_date,
        "product_name": product_name,
        "bounds": {
            "north": region['north'],
            "south": region['south'],
            "east": region['east'],
            "west": region['west']
        },
        "source": "downloaded"
    }


def download_all_satellite_images(region: dict, date_range: dict, layers: list = None, max_cloud: int = 35, max_images: int = 10):
    """
    Download ALL Sentinel-2 images for the date range using OData API with pagination.
    Downloads images for each requested layer.

    Args:
        region: Geographic bounds
        date_range: Start and end dates
        layers: List of layer types to download (e.g., ['truecolor', 'ndvi', 'nbr'])
        max_cloud: Maximum cloud coverage percentage
        max_images: Maximum number of products to download (per layer)

    Returns:
        List of image metadata dictionaries
    """
    # Default to truecolor if no layers specified
    if not layers:
        layers = ['truecolor']

    print("🔑 Obtaining Copernicus token...")
    token = get_copernicus_token()
    print("✅ Token acquired")
    
    # Query all products with pagination
    products = query_sentinel_products_with_pagination(region, date_range, token, max_cloud)
    
    if not products:
        print("⚠️ No products found matching criteria")
        return []
    
    # Limit downloads to avoid overwhelming the system
    products_to_download = products[:max_images]
    total_downloads = len(products_to_download) * len(layers)
    print(f"\n📥 Downloading {total_downloads} image(s): {len(products_to_download)} products × {len(layers)} layers")
    print(f"   Layers: {', '.join(layers)}")

    downloaded_images = []
    failed_count = 0
    
    for idx, product in enumerate(products_to_download, 1):
        # Download each layer for this product
        for layer in layers:
            try:
                print(f"\n🖼️  Image {idx}/{len(products_to_download)} - Layer: {layer.upper()}")
                print(f"   Product: {product.get('Name', 'unknown')}")

                img_meta = download_satellite_image_for_product(product, region, token, layer, max_cloud)
                img_meta['layer'] = layer  # Add layer info to metadata
                downloaded_images.append(img_meta)

                print(f"   ✅ Downloaded: {img_meta['filename']} ({img_meta['size_kb']} KB)")

            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed to download {layer}: {str(e)}")

    print(f"\n📊 Download Summary: {len(downloaded_images)} succeeded, {failed_count} failed")
    return downloaded_images


COPERNICUS_USERNAME = os.getenv("COPERNICUS_USERNAME")
COPERNICUS_PASSWORD = os.getenv("COPERNICUS_PASSWORD")


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

        # Attempt to download ALL images from the date range with pagination
        downloaded_images = []
        download_error = None
        print("\n🛰️ Downloading ALL Sentinel-2 images for date range (with pagination)...")
        print(f"   📅 Date Range: {date_range['start']} to {date_range['end']}")
        print(f"   🎨 Layers: {', '.join(layers) if layers else 'truecolor (default)'}")
        try:
            downloaded_images = download_all_satellite_images(region, date_range, layers=layers, max_cloud=15, max_images=10)
        except Exception as dl_err:
            download_error = str(dl_err)
            print(f"⚠️ Download failed: {download_error}")

        # Existing local images (cache)
        cached_images = []
        for filename in all_files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(SATELLITE_DATA_DIR, filename)
                size_kb = os.path.getsize(file_path) / 1024
                url = f"/satellite_data/{filename}"
                cached_images.append({
                    "filename": filename,
                    "url": url,
                    "size_kb": round(size_kb, 2),
                    "bounds": {
                        "north": region['north'],
                        "south": region['south'],
                        "east": region['east'],
                        "west": region['west']
                    },
                    "source": "cached"
                })

        # Combine downloaded and cached images
        images_meta = downloaded_images + cached_images
        
        print(f"\n📊 IMAGE COUNT SUMMARY:")
        print(f"   Downloaded images: {len(downloaded_images)}")
        print(f"   Cached images: {len(cached_images)}")
        print(f"   📸 TOTAL IMAGES RETURNED: {len(images_meta)}")

        if not images_meta:
            print(f"\n❌ [ERROR] No satellite images found!")
            print("="*80 + "\n")
            return jsonify({
                "success": False,
                "message": "No satellite images available (download failed and cache empty).",
                "download_error": download_error,
                "images": []
            }), 404

        print(f"\n✅ [SUCCESS] Returning {len(images_meta)} image(s)")
        for idx, img in enumerate(images_meta, 1):
            sensing = img.get('sensing_date', 'unknown')
            print(f"   Image {idx}: {img['filename']} ({img['size_kb']} KB) - Date: {sensing} - Source: {img['source']}")
        print("="*80 + "\n")

        return jsonify({
            "success": True,
            "message": f"Found {len(images_meta)} satellite image(s)",
            "download_error": download_error,
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

        # Step 4: Select images (before and after for same filter type)
        print(f"\n🔍 [DEBUG] Step 4: Selecting images to analyze (before/after)...")
        
        # Group images by filter type (extract from filename pattern: sentinel2_DATE_FILTER_HASH)
        images_by_filter = {}
        for img in available_images:
            parts = img.split('_')
            if len(parts) >= 3:
                filter_type = parts[2]  # e.g., 'ndvi', 'dnbr', 'truecolor', etc.
                if filter_type not in images_by_filter:
                    images_by_filter[filter_type] = []
                images_by_filter[filter_type].append(img)
        
        print(f"   Images grouped by filter type: {dict((k, len(v)) for k, v in images_by_filter.items())}")
        
        # Use selected layers from frontend to determine which filter to use
        selected_filter = None
        selected_images = []
        
        # Priority 1: Use the first selected layer from frontend that has images
        if layers:
            print(f"   Checking selected layers from frontend: {layers}")
            for layer in layers:
                if layer in images_by_filter and len(images_by_filter[layer]) >= 2:
                    selected_filter = layer
                    selected_images = sorted(images_by_filter[layer])  # Sort by date (in filename)
                    print(f"   ✅ Using selected layer '{layer}' with {len(selected_images)} images")
                    break
            
            # Fallback: if no selected layer has >=2 images, try single image
            if not selected_filter:
                for layer in layers:
                    if layer in images_by_filter:
                        selected_filter = layer
                        selected_images = sorted(images_by_filter[layer])
                        print(f"   ⚠️ Using selected layer '{layer}' with only {len(selected_images)} image(s)")
                        break
        
        # Priority 2: If no layers selected or no matching images, use any filter with >=2 images
        if not selected_filter:
            print(f"   No matching selected layers, searching for any filter with multiple images...")
            for filter_type, imgs in images_by_filter.items():
                if len(imgs) >= 2:
                    selected_filter = filter_type
                    selected_images = sorted(imgs)
                    print(f"   ✅ Fallback to '{filter_type}' with {len(selected_images)} images")
                    break
        
        # Priority 3: Last resort - use any available filter
        if not selected_filter and images_by_filter:
            selected_filter = list(images_by_filter.keys())[0]
            selected_images = sorted(images_by_filter[selected_filter])
            print(f"   ⚠️ Last resort: using '{selected_filter}' with {len(selected_images)} image(s)")
        
        # Select first (oldest) and last (newest) images
        if len(selected_images) >= 2:
            image_before = selected_images[0]
            image_after = selected_images[-1]
            image_paths = [
                os.path.join(SATELLITE_DATA_DIR, image_before),
                os.path.join(SATELLITE_DATA_DIR, image_after)
            ]
            print(f"   ✅ Selected filter type: {selected_filter}")
            print(f"   ✅ Before image: {image_before}")
            print(f"   ✅ After image: {image_after}")
            images_analyzed = f"{image_before}, {image_after}"
            
            # Extract dates from filenames (format: sentinel2_YYYYMMDD_FILTER_HASH)
            date_before = image_before.split('_')[1] if len(image_before.split('_')) > 1 else 'unknown'
            date_after = image_after.split('_')[1] if len(image_after.split('_')) > 1 else 'unknown'
            
            # Format dates as YYYY-MM-DD
            if len(date_before) == 8:
                date_before_formatted = f"{date_before[:4]}-{date_before[4:6]}-{date_before[6:8]}"
            else:
                date_before_formatted = date_before
            
            if len(date_after) == 8:
                date_after_formatted = f"{date_after[:4]}-{date_after[4:6]}-{date_after[6:8]}"
            else:
                date_after_formatted = date_after
                
        else:
            # Only one image available
            image_filename = selected_images[0]
            image_paths = [os.path.join(SATELLITE_DATA_DIR, image_filename)]
            print(f"   ⚠️ Only one image available: {image_filename}")
            images_analyzed = image_filename
            
            # Extract date from filename
            date_single = image_filename.split('_')[1] if len(image_filename.split('_')) > 1 else 'unknown'
            if len(date_single) == 8:
                date_single_formatted = f"{date_single[:4]}-{date_single[4:6]}-{date_single[6:8]}"
            else:
                date_single_formatted = date_single

        # Step 5: Build enhanced prompt
        print(f"\n🔍 [DEBUG] Step 5: Building enhanced prompt...")
        
        if len(image_paths) == 2:
            image_context = f"Two satellite images of the selected region:\n  - BEFORE image: {date_before_formatted} ({selected_filter.upper()} filter)\n  - AFTER image: {date_after_formatted} ({selected_filter.upper()} filter)"
            analysis_instruction = f"Compare the two {selected_filter.upper()} images captured on {date_before_formatted} (BEFORE) and {date_after_formatted} (AFTER). Analyze the changes over time between these specific dates. Focus on temporal changes, vegetation recovery, burn progression, or environmental shifts."
        else:
            image_context = f"Satellite image captured on {date_single_formatted} using {selected_filter.upper()} filter"
            analysis_instruction = f"Analyze the {selected_filter.upper()} image from {date_single_formatted} and provide detailed observations."
        
        enhanced_prompt = f"""You are FireDoc VLM, an expert AI assistant for analyzing satellite imagery to assess wildfire burn severity and environmental impact.

User's Question: {prompt}

Context:
- Images: {image_context}
- Region Coordinates: North {region['north']}°, South {region['south']}°, East {region['east']}°, West {region['west']}°

{analysis_instruction}

Please provide a detailed, helpful response focusing on:
- Burn severity and changes over time (if applicable)
- Vegetation health and recovery
- Environmental impact assessment
- Any visible patterns, anomalies, or temporal changes

Be specific and use quantitative observations when possible. Reference the specific dates mentioned above in your analysis. Keep your answers concise (max 6-8 sentences) and formatted in markdown."""

        print(f"   ✅ Enhanced prompt built ({len(enhanced_prompt)} characters)")

        # Step 6: Call AI analysis
        print(f"\n🔍 [DEBUG] Step 6: Calling AI analysis function...")
        ai_response = analyze_image_with_vlm(image_paths, enhanced_prompt, conversation_history)

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
            "images_analyzed": images_analyzed,
            "comparison_mode": len(image_paths) == 2
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
