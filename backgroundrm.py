import os
import replicate
import requests
from io import BytesIO
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackgroundRemover:
    def __init__(self):
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("Replicate API token not found. Please set REPLICATE_API_TOKEN environment variable.")
        os.environ["REPLICATE_API_TOKEN"] = self.api_token

    def remove_background(self, image_url, output_path):
        try:
            output = replicate.run(
                "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
                input={
                    "image": image_url,
                    "format": "png",
                    "reverse": False,
                    "threshold": 0,
                    "background_type": "rgba"
                }
            )
            
            # Download the processed image
            response = requests.get(output)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.save(output_path)
                logger.info(f"Background removed image saved to {output_path}")
                return True
            else:
                logger.error(f"Failed to download processed image: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing background: {str(e)}")
            return False

def process_image(image_url, output_filename):
    remover = BackgroundRemover()
    output_path = f"processed_images/{output_filename}"
    
    # Create output directory if it doesn't exist
    os.makedirs("processed_images", exist_ok=True)
    
    success = remover.remove_background(image_url, output_path)
    return output_path if success else None
