# Flask + Hugging Face LLM API

A simple Flask application that connects to Hugging Face's Inference API to execute prompts with Large Language Models.

## Features

- Flask REST API endpoints
- Integration with Hugging Face Inference API
- Uses Llama-3.2-3B-Instruct model (can be easily changed)
- Configurable parameters (temperature, max tokens)
- Environment variable configuration for API tokens

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Hugging Face API Token

1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new access token (read access is sufficient)
3. Copy the token

### 3. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your token
# HUGGINGFACE_API_TOKEN=hf_your_actual_token_here
```

### 4. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### GET `/`
Returns API information and available endpoints.

```bash
curl http://localhost:5000/
```

### GET `/health`
Health check endpoint.

```bash
curl http://localhost:5000/health
```

### POST `/generate`
Generate text based on a prompt.

**Request Body:**
```json
{
  "prompt": "What is the capital of France?",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing in simple terms"}'
```

**Response:**
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "response": [
    {
      "generated_text": "Quantum computing uses quantum mechanics principles..."
    }
  ],
  "model": "Llama-3.2-3B-Instruct"
}
```

## Configuration

### Change the Model

Edit `app.py` and modify the `HF_API_URL` variable to use a different model:

```python
HF_API_URL = "https://api-inference.huggingface.co/models/YOUR_MODEL_NAME"
```

Popular models:
- `meta-llama/Llama-3.2-3B-Instruct` (default)
- `mistralai/Mistral-7B-Instruct-v0.2`
- `google/flan-t5-large`
- `microsoft/phi-2`

### Adjust Parameters

When calling `/generate`, you can customize:
- `max_tokens`: Maximum number of tokens to generate (default: 500)
- `temperature`: Controls randomness, 0.0-1.0 (default: 0.7)

## Notes

- First request to a model may take longer (model loading time)
- Free tier has rate limits
- Some models may require additional Hugging Face permissions

## Troubleshooting

**"Model is loading" error**: Wait a few seconds and retry. Cold starts can take 20-60 seconds.

**401 Unauthorized**: Check your API token is correctly set in `.env`

**503 Service Unavailable**: The model might be overloaded. Try again in a few moments.
