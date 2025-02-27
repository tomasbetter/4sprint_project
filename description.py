import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_description(brand, product_name):
    api_key = os.getenv("OPENAI_API_KEY")  # Get API key securely
    if not api_key:
        raise ValueError("OpenAI API key is missing. Set the environment variable OPENAI_API_KEY.")

    client = openai.OpenAI(api_key=api_key)

    prompt = f"Generate a concise, one-paragraph description for a {brand} product named {product_name}. The description should be brief but informative."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Description not available"
