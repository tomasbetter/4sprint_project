import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_category_level_2(product_name, description, category_level_1):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is missing. Set the environment variable OPENAI_API_KEY.")

    client = openai.OpenAI(api_key=api_key)

    category_hierarchy = {
        "Bakery": [
            "Fresh Bread", "Pastries", "Cakes", "Baking Ingredients", 
            "Specialty Breads", "Gluten-free Products"
        ],
        "Fresh Produce": [
            "Fresh Vegetables", "Fresh Fruits", "Fresh Herbs", "Mushrooms", 
            "Sprouts & Microgreens", "Pre-cut & Prepared Produce"
        ],
        "Meat & Poultry": [
            "Fresh Beef", "Fresh Pork", "Fresh Lamb", "Fresh Poultry (Chicken, Turkey, Duck)", 
            "Processed Meats & Deli", "Game Meat", "Plant-based Meat Alternatives"
        ],
        "Seafood": [
            "Fresh Fish", "Fresh Shellfish", "Frozen Seafood", 
            "Processed Seafood", "Dried Seafood", "Live Seafood"
        ],
        "Dairy & Eggs": [
            "Milk & Cream", "Cheese", "Butter & Spreads", 
            "Yogurt & Cultured Products", "Eggs & Egg Products", "Plant-based Dairy Alternatives"
        ],
        "Dry Goods & Pantry": [
            "Rice & Grains", "Pasta & Noodles", "Flour & Baking Ingredients", 
            "Canned & Jarred Goods", "Oils & Vinegars", "Dried Beans & Legumes", 
            "Nuts & Seeds", "Spices & Seasonings"
        ],
        "Beverages": [
            "Coffee & Tea", "Soft Drinks", "Juices", "Water & Sparkling Water", 
            "Energy & Sports Drinks", "Alcoholic Beverages", "Beverage Syrups & Concentrates"
        ],
        "Frozen Food": [
            "Frozen Vegetables", "Frozen Fruits", "Frozen Meals", 
            "Frozen Meat & Poultry", "Ice Cream & Frozen Desserts", "Frozen Bakery Products"
        ],
        "Condiments & Souces": [
            "Table Sauces", "Cooking Sauces", "Dressings & Marinades", 
            "Dips & Spreads", "Asian Sauces & Condiments", "Herbs & Spice Pastes"
        ],
        "Confectionery & Sweets": [
            "Chocolate", "Candy & Gums", "Baked Sweets", 
            "Ice Cream & Frozen Treats", "Dessert Ingredients", "Traditional Sweets"
        ],
        "Snacks": [
            "Chips & Crisps", "Nuts & Seeds", "Crackers & Biscuits", 
            "Dried Fruits", "Trail Mixes", "Protein & Energy Bars", "Popcorn & Corn Snacks"
        ]
    }
    
    if category_level_1 not in category_hierarchy:
        return "Uncategorized"
    
    subcategories = category_hierarchy[category_level_1]
    prompt = (
        f"Based on the following product information, select the most appropriate subcategory from the list provided:\n\n"
        f"Product Name: {product_name}\n"
        f"Description: {description}\n"
        f"Main Category: {category_level_1}\n\n"
        f"Subcategories: {', '.join(subcategories)}\n\n"
        f"Please provide only the subcategory name as your answer."
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
