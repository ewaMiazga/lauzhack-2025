from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Hugging Face API configuration
HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

def query_huggingface(prompt, max_tokens=500, temperature=0.7):
    """
    Send a prompt to Hugging Face's Inference API
    
    Args:
        prompt (str): The text prompt to send to the LLM
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Controls randomness (0.0-1.0)
    
    Returns:
        dict: Response from the API or error message
    """
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Hugging Face LLM API",
        "endpoints": {
            "/generate": "POST - Generate text from a prompt",
            "/health": "GET - Check API health"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model": "Llama-3.2-3B-Instruct"})

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate text based on a prompt
    
    Expected JSON body:
    {
        "prompt": "Your prompt here",
        "max_tokens": 500 (optional),
        "temperature": 0.7 (optional)
    }
    """
    if not HF_API_TOKEN:
        return jsonify({
            "error": "Hugging Face API token not configured. Please set HUGGINGFACE_API_TOKEN in .env file"
        }), 500
    
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400
    
    prompt = data['prompt']
    max_tokens = data.get('max_tokens', 500)
    temperature = data.get('temperature', 0.7)
    
    # Query Hugging Face API
    result = query_huggingface(prompt, max_tokens, temperature)
    
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify({
        "prompt": prompt,
        "response": result,
        "model": "Llama-3.2-3B-Instruct"
    })

if __name__ == '__main__':
    if not HF_API_TOKEN:
        print("WARNING: HUGGINGFACE_API_TOKEN not set in environment variables")
        print("Please create a .env file with your Hugging Face API token")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
