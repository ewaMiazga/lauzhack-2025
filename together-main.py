from together import Together
from dotenv import load_dotenv
import os
import base64

def encode_image(image_path: str) -> str:
    """Read an image file and return a base64-encoded string.
    Raises FileNotFoundError if the path does not exist.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main():
    # Load variables from .env into environment
    load_dotenv()

    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY not found. Add it to a .env file.")

    # Resolve image path (works regardless of current working directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "images", "car.jpg")

    # Prepare prompt and encoded image
    prompt = "what car brand is it?"
    base64_image = encode_image(image_path)

    client = Together(api_key=api_key)

    # Create a streaming chat completion with an image
    stream = client.chat.completions.create(
        model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"  # car.jpg assumed JPEG
                        },
                    },
                ],
            }
        ],
        stream=True,
    )

    print("\n--- MODEL RESPONSE (streaming) ---")
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n--- END ---")


if __name__ == "__main__":
    main()
