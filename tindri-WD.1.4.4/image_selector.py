import os
import cv2
import numpy as np
import csv
import requests
import pandas as pd
from PIL import Image
from pathlib import Path
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_KEY = "AIzaSyDPoKBAmGCz1Qly5qOVsEHBw57TWhdVE4g"
CX = "56be6c13292f14170"
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

class ProductImageSelector:
    """
    A class to select the best product image for marketplace listings based on:
    1. White/bright background (mandatory)
    2. Largest object/product size in the image
    3. Image quality (sharpness, resolution)
    """
    
    def __init__(self, input_csv, output_csv, min_background_brightness=180):
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.min_background_brightness = min_background_brightness
        self.temp_dir = Path("temp_images")
        os.makedirs(self.temp_dir, exist_ok=True)

    def load_image_from_url(self, url):
        """Load image from URL and return as OpenCV image"""
        try:
            response = requests.get(url, timeout=10)
            img = Image.open(BytesIO(response.content))
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.warning(f"Could not load image from {url}: {e}")
            return None

    def check_background_brightness(self, img):
        """Check if the image has a white/bright background"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
            
        _, bright_mask = cv2.threshold(gray, self.min_background_brightness, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(gray, 50, 150)
        dilated_edges = cv2.dilate(edges, np.ones((5,5), np.uint8), iterations=1)
        background_mask = cv2.bitwise_and(bright_mask, bright_mask, mask=cv2.bitwise_not(dilated_edges))
        
        background_percentage = np.sum(background_mask > 0) / (background_mask.shape[0] * background_mask.shape[1])
        # Use numpy masked array to calculate mean of background pixels
        masked_gray = np.ma.array(gray, mask=(background_mask == 0))
        avg_background_brightness = masked_gray.mean() if np.any(background_mask > 0) else 0
        
        background_score = background_percentage * (avg_background_brightness / 255) * 10
        has_bright_background = background_percentage > 0.3 and avg_background_brightness > self.min_background_brightness
        
        return has_bright_background, background_score, background_mask

    def get_object_size(self, img, background_mask):
        """Calculate the absolute size of the main object in the image (in pixels)"""
        object_mask = cv2.bitwise_not(background_mask)
        kernel = np.ones((5,5), np.uint8)
        object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, kernel)
        object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0, 0, None
        
        largest_contour = max(contours, key=cv2.contourArea)
        object_area_pixels = cv2.contourArea(largest_contour)
        img_area = img.shape[0] * img.shape[1]
        object_percentage = object_area_pixels / img_area
        
        return object_area_pixels, object_percentage, largest_contour

    def get_image_quality_score(self, img):
        """Calculate image quality score based on sharpness and resolution"""
        height, width = img.shape[:2]
        resolution_score = min(10, width * height / 1000000)
        
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
            
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(10, laplacian_var / 100)
        
        quality_score = (0.6 * sharpness_score) + (0.4 * resolution_score)
        return quality_score

    def evaluate_image(self, url):
        """Evaluate an image based on background, object size, and quality"""
        # Ignore images from the specified domain
        if url.startswith("https://images.openfoodfacts.org"):
            logger.info(f"Ignoring image from domain: {url}")
            return False, 0, 0, 0, None, 0
        
        img = self.load_image_from_url(url)
        if img is None:
            return False, 0, 0, 0, None, 0
            
        has_bright_bg, bg_score, background_mask = self.check_background_brightness(img)
        
        if not has_bright_bg:
            return False, 0, 0, 0, None, bg_score
        
        object_area_pixels, object_percentage, largest_contour = self.get_object_size(img, background_mask)
        quality_score = self.get_image_quality_score(img)
        
        return has_bright_bg, object_area_pixels, quality_score, object_percentage, largest_contour, bg_score

    def select_best_images(self):
        """Process CSV and select the best image for each product"""
        df = pd.read_csv(self.input_csv)
        results = []
        
        for (brand, product_name), group in df.groupby(['brand', 'product_name']):
            logger.info(f"Processing product: {brand} - {product_name}")
            
            bright_bg_images = []
            scores_table = []
            
            for _, row in group.iterrows():
                url = row['image_url']
                has_bright_bg, object_area_pixels, quality_score, obj_pct, _, bg_score = self.evaluate_image(url)
                
                status = "✓" if has_bright_bg else "✗"
                scores_table.append((
                    url, status, object_area_pixels, 
                    round(quality_score, 2), f"{obj_pct:.1%}", round(bg_score, 2)
                ))
                
                if has_bright_bg:
                    bright_bg_images.append((url, object_area_pixels, quality_score, bg_score))
            
            bright_bg_images.sort(key=lambda x: x[1], reverse=True)
            
            best_image_url = None
            if bright_bg_images:
                best_image_url, largest_object_size, quality_score, bg_score = bright_bg_images[0]
                
                similar_size_images = [
                    (url, size, q_score, b_score) for url, size, q_score, b_score in bright_bg_images
                    if size >= largest_object_size * 0.95
                ]
                
                if len(similar_size_images) > 1:
                    weighted_scores = []
                    for url, size, q_score, b_score in similar_size_images:
                        norm_size = size / largest_object_size
                        weighted_score = (0.7 * norm_size) + (0.2 * q_score / 10) + (0.1 * b_score / 10)
                        weighted_scores.append((url, weighted_score))
                    
                    best_image_url, _ = max(weighted_scores, key=lambda x: x[1])
            
            logger.info(f"Scores for {brand} - {product_name}:")
            for score_row in sorted(scores_table, key=lambda x: x[2] if x[1] == "✓" else 0, reverse=True):
                logger.info(f"  {score_row[0]}: {score_row[1]} {score_row[2]} (q:{score_row[3]}, {score_row[4]}, bg:{score_row[5]})")
            
            if best_image_url:
                logger.info(f"Selected best image for {brand} - {product_name}: {best_image_url}")
                results.append({
                    'brand': brand,
                    'product_name': product_name,
                    'image_url': best_image_url
                })
            else:
                logger.warning(f"No suitable image found for {brand} - {product_name}")
        
        pd.DataFrame(results).to_csv(self.output_csv, index=False)
        logger.info(f"Saved best images to {self.output_csv}")


def search_images(query, num_results=10):
    all_items = []
    for i in range(0, num_results, 5):
        params = {"q": query, "cx": CX, "key": API_KEY, "searchType": "image", "num": min(5, num_results - i), "start": i+1}
        response = requests.get(SEARCH_URL, params=params)
        if response.status_code == 200:
            all_items.extend(response.json().get("items", []))
        else:
            print(f"Error fetching images for {query}: {response.status_code}")
            break
    return all_items[:num_results]


def fetch_images(input_csv, output_csv):
    if not os.path.exists(input_csv):
        print(f"Input file {input_csv} not found!")
        return

    results = []
    with open(input_csv, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            query = f"{row['brand']} {row['product_name']}"
            print(f"Searching images for: {query}")
            for image in search_images(query, num_results=10):
                results.append({"brand": row['brand'], "product_name": row['product_name'], "image_url": image.get("link")})

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["brand", "product_name", "image_url"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Image search results saved to {output_csv}")


if __name__ == "__main__":
    # Example usage when run directly
    fetch_images("updated_all_products.csv", "image_search_results.csv")
    selector = ProductImageSelector("image_search_results.csv", "best_images.csv")
    selector.select_best_images()