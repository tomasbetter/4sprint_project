import sys
import pandas as pd
from description import create_description
from category1 import create_category_level_1
from category2 import create_category_level_2
from dotenv import load_dotenv
import os
from image_search import fetch_images
from image_selector import ProductImageSelector
from backgroundrm import process_image
from image_to_brand import get_brand_and_product
from openai import OpenAI
import json

# Load environment variables from .env
load_dotenv()

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_url>")
        return

    image_url = sys.argv[1]
    
    # Retrieve API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is missing. Set the environment variable OPENAI_API_KEY.")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Extract brand and product name from image
    brand, product_name = get_brand_and_product(client, image_url)
    
    if not brand or not product_name:
        print("Failed to identify brand and product name. Exiting.")
        return

    print(f"Identified Brand: {brand}, Product Name: {product_name}")

    # Generate description
    description = create_description(brand, product_name)

    # Generate category level 1
    category_level_1 = create_category_level_1(brand, product_name, description)
    
    # Generate category level 2
    category_level_2 = create_category_level_2(product_name, description, category_level_1)

    # Step 1: Create temporary CSV with product info
    temp_input_csv = "temp_product.csv"
    pd.DataFrame({"brand": [brand], "product_name": [product_name]}).to_csv(temp_input_csv, index=False)

    # Step 2: Fetch images using the separated image_search module
    temp_images_csv = "temp_images.csv"
    fetch_images(input_csv=temp_input_csv, output_csv=temp_images_csv)
    
    # Step 3: Select the best image using the separated image_selector module
    temp_best_image_csv = "temp_best_image.csv"
    selector = ProductImageSelector(input_csv=temp_images_csv, output_csv=temp_best_image_csv)
    selector.select_best_images()
    
    # Check if temp_best_image.csv exists and has content
    if os.path.exists(temp_best_image_csv) and os.stat(temp_best_image_csv).st_size > 0:
        best_image_df = pd.read_csv(temp_best_image_csv)
        best_image_url = best_image_df['image_url'].iloc[0] if not best_image_df.empty else None
    else:
        print("Error: No images found. Exiting.")
        return
    
    processed_image_path = None
    if best_image_url:
        processed_filename = f"{brand}_{product_name.replace(' ', '_')}.png"
        processed_image_path = process_image(best_image_url, processed_filename)
        print(f"Image processed and saved to: {processed_image_path}")

    # Clean up temporary files
    for temp_file in [temp_input_csv, temp_images_csv, temp_best_image_csv]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    # Load existing CSV or create new one
    try:
        data = pd.read_csv("data.csv")
    except FileNotFoundError:
        data = pd.DataFrame(columns=["brand", "product_name", "description", "category1", "category2", "image_url", "processed_image_path"])

    new_entry = pd.DataFrame({
        "brand": [brand],
        "product_name": [product_name],
        "description": [description],
        "category1": [category_level_1],
        "category2": [category_level_2],
        "image_url": [best_image_url],
        "processed_image_path": [processed_image_path]
    })
    
    data = pd.concat([data, new_entry], ignore_index=True)
    data.to_csv("data.csv", index=False)

if __name__ == "__main__":
    main()