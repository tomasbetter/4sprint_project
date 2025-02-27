import os
import csv
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_KEY = "AIzaSyDPoKBAmGCz1Qly5qOVsEHBw57TWhdVE4g"
CX = "56be6c13292f14170"
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

def search_images(query, num_results=10):
    """
    Search for images using Google Custom Search API
    
    Args:
        query (str): The search query
        num_results (int): Number of images to return
    
    Returns:
        list: List of image items
    """
    all_items = []
    for i in range(0, num_results, 5):
        params = {
            "q": query, 
            "cx": CX, 
            "key": API_KEY, 
            "searchType": "image", 
            "num": min(5, num_results - i), 
            "start": i+1
        }
        response = requests.get(SEARCH_URL, params=params)
        if response.status_code == 200:
            all_items.extend(response.json().get("items", []))
        else:
            logger.error(f"Error fetching images for {query}: {response.status_code}")
            break
    return all_items[:num_results]


def fetch_images(input_csv, output_csv):
    """
    Fetch images for products listed in input CSV and save results to output CSV
    
    Args:
        input_csv (str): Path to input CSV with 'brand' and 'product_name' columns
        output_csv (str): Path to output CSV where results will be saved
    """
    if not os.path.exists(input_csv):
        logger.error(f"Input file {input_csv} not found!")
        return

    results = []
    with open(input_csv, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            query = f"{row['brand']} {row['product_name']}"
            logger.info(f"Searching images for: {query}")
            for image in search_images(query, num_results=10):
                results.append({
                    "brand": row['brand'], 
                    "product_name": row['product_name'], 
                    "image_url": image.get("link")
                })

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["brand", "product_name", "image_url"])
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Image search results saved to {output_csv}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python image_search.py <input_csv> <output_csv>")
        sys.exit(1)
        
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    fetch_images(input_csv, output_csv)