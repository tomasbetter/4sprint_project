import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_category_level_1(brand, product_name, description):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is missing. Set the environment variable OPENAI_API_KEY.")

    client = openai.OpenAI(api_key=api_key)

    categories = [
        "Bakery", "Fresh Produce", "Meat & Poultry", "Seafood",
        "Dairy & Eggs", "Dry Goods & Pantry", "Beverages",
        "Frozen Food", "Condiments & Sauces", "Confectionery & Sweets", "Snacks"
    ]

    prompt = (
        f"Based on the following product information, select the most appropriate category from the list provided:\n\n"
        f"Brand: {brand}\n"
        f"Product Name: {product_name}\n"
        f"Description: {description}\n\n"
        f"Categories: {', '.join(categories)}\n\n"
        f"Please provide only the category name as your answer."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Uncategorized"
