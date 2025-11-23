from copernicusapi import QueryConstructor
from shapely.geometry import Polygon
from datetime import datetime
import requests
import os
from dotenv import load_dotenv


# Copernicus Data Space credentials
load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise ValueError("TOGETHER_API_KEY not found. Add it to a .env file.")

# Initialize the query constructor
query_constructor = QueryConstructor()

# Define the area of interest (bounding box: minLon, minLat, maxLon, maxLat)
aoi = Polygon([
    (13.0, 45.5),
    (13.5, 45.5),
    (13.5, 46.0),
    (13.0, 46.0),
    (13.0, 45.5)
])

# Build the query
query_constructor.add_collection_filter('sentinel-2')
query_constructor.add_product_type_filter('l2a')
query_constructor.add_aoi_filter(aoi)
query_constructor.add_sensing_start_date_filter(datetime(2023, 10, 1), datetime(2023, 10, 31))
query_constructor.add_cloud_cover_filter(5)  # Max 5% cloud cover (minimal clouds)

# Check how many products match
print("Checking query...")
n_products = query_constructor.check_query()
print(f"Found {n_products} products matching the query")

# Send the query to get the products
print("\nRetrieving product list...")
products, result = query_constructor.send_query()

# Display the first few products
print("\nAvailable products:")
print(products[['file_name', 'cloud_cover', 'sensing_start_date', 'file_size']].head())

# To download a product, you'll need to authenticate and download
# Here's an example of how to download the first product:
if len(products) > 0:
    print("\n" + "="*60)
    print("To download products, you need to:")
    print("1. Register at https://dataspace.copernicus.eu/")
    print("2. Get your credentials")
    print("3. Use the download_url from the products dataframe")
    print("="*60)
    
    # Show the download URL for the first product
    first_product = products.iloc[0]
    print(f"\nFirst product: {first_product['file_name']}")
    print(f"Download URL: {first_product['download_url']}")
    print(f"File size: {first_product['file_size']:.2f} MB")
    print(f"Cloud cover: {first_product['cloud_cover']:.1f}%")

    # Create a directory to save downloaded files
    download_dir = "/Users/ewamiazga/Desktop/studies/lauzhack-2025/satellite_data"
    os.makedirs(download_dir, exist_ok=True)
    print(f"\nDownload directory: {download_dir}")
    
    # Authenticate with Copernicus Data Space
    print("\nAuthenticating with Copernicus Data Space...")
    token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    token_response = requests.post(
        token_url,
        data={
            "grant_type": "password",
            "username": USERNAME,
            "password": PASSWORD,
            "client_id": "cdse-public"
        }
    )
    
    if token_response.status_code != 200:
        print(f"❌ Authentication failed: {token_response.text}")
        exit(1)
    
    access_token = token_response.json()["access_token"]
    print("✅ Authentication successful!")
    
    # Use Sentinel Hub Processing API to download a JPEG image instead of the full product
    print("\n" + "="*60)
    print("Downloading processed JPEG image (much smaller)...")
    print("="*60)
    
    # Define the evalscript for true color RGB image
    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: ["B04", "B03", "B02"],
        output: {
          bands: 3,
          sampleType: "AUTO"
        }
      };
    }
    
    function evaluatePixel(sample) {
      return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
    }
    """
    
    # Get the sensing date from the first product
    sensing_date = first_product['sensing_start_date'].strftime('%Y-%m-%d')
    
    # Build the Sentinel Hub Processing API request
    process_url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    
    processing_payload = {
        "input": {
            "bounds": {
                "bbox": [13.0, 45.5, 13.5, 46.0]
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{sensing_date}T00:00:00Z",
                        "to": f"{sensing_date}T23:59:59Z"
                    },
                    "maxCloudCoverage": 5
                }
            }]
        },
        "output": {
            "width": 2048,
            "height": 2048,
            "responses": [{
                "identifier": "default",
                "format": {
                    "type": "image/jpeg"
                }
            }]
        },
        "evalscript": evalscript
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "image/jpeg"
    }
    
    print(f"\nRequesting image for date: {sensing_date}")
    print(f"Cloud cover: {first_product['cloud_cover']:.1f}%")
    print(f"Output size: 2048x2048 pixels")
    
    response = requests.post(process_url, headers=headers, json=processing_payload)
    
    if response.status_code == 200:
        # Save the JPEG image
        image_filename = f"sentinel2_{sensing_date.replace('-', '')}.jpg"
        image_path = os.path.join(download_dir, image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        file_size_kb = len(response.content) / 1024
        print(f"\n✅ Downloaded JPEG image successfully!")
        print(f"   File: {image_path}")
        print(f"   Size: {file_size_kb:.1f} KB")
    else:
        print(f"\n❌ Download failed: {response.status_code}")
        print(f"Error: {response.text}")
        