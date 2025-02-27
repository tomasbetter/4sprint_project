import openai
import sys
import time
import os
import json
import base64
import requests
from openai import OpenAI

def image_to_base64(image_url):
    """
    Downloads an image from a URL and converts it to a base64-encoded string.
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
        else:
            print(f"Failed to fetch image: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
        return None

def get_brand_and_product(client, image_url):
    """
    Identify the brand and product name from an image.
    Converts the image to a base64 string for OpenAI API.
    """
    image_base64 = image_to_base64(image_url)
    if not image_base64:
        return None, None  # Exit if image fetching fails
    
    prompt = """Identify the brand and product name from this image.
    Return a JSON object in the format:
    {
        "brand": "<brand_name>",
        "product_name": "<product_name>"
    }
    Ensure the response is strictly in English."""
    
    max_retries = 3
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Ensure responses are strictly in JSON format."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_base64}}
                    ]}
                ],
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            print(f"Raw OpenAI Response: {content}")  # Debugging log
            
            try:
                data = json.loads(content)
                brand = data.get("brand", "").strip()
                product_name = data.get("product_name", "").strip()
            except json.JSONDecodeError:
                print("Error: Response is not in JSON format.")
                return None, None
            
            if not brand or not product_name:
                print("Error: Brand or product name not detected properly.")
                return None, None
            
            return brand, product_name
            
        except Exception as e:
            current_retry += 1
            print(f"Error occurred: {str(e)}. Retrying... Attempt {current_retry}/{max_retries}")
            time.sleep(5 * current_retry)

    print("Failed after maximum retry attempts.")
    return None, None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python image_to_brand.py <image_url>")
        sys.exit(1)
    
    image_url = sys.argv[1]
    
    # Retrieve API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is missing. Set the environment variable OPENAI_API_KEY.")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    brand, product_name = get_brand_and_product(client, image_url)
    
    if brand and product_name:
        print(f"Brand: {brand}")
        print(f"Product Name: {product_name}")
    else:
        print("Failed to extract brand and product name.")
