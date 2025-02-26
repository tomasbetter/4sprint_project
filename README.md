# Product Categorization and Image Processing Pipeline

## Overview
This project is an automated pipeline that processes product images, extracts brand and product names, generates descriptions, assigns product categories, selects the best product image, and removes image backgrounds. It integrates OpenAI's API for text processing and categorization, as well as Replicate API for background removal.

## Features
- **Extract Brand & Product Name**: Uses OpenAI API to identify the brand and product name from an image.
- **Generate Product Description**: Creates a short and informative description using AI.
- **Categorize Products**: Assigns a primary and secondary category based on the product description.
- **Fetch & Select Best Image**: Searches for relevant product images using Google Custom Search API and selects the best one based on quality and background.
- **Background Removal**: Processes selected images to remove backgrounds for better presentation.
- **Data Storage**: Stores product details in a CSV file for future reference.

## File Structure
- `main.py` - The main script that orchestrates the entire pipeline.
- `image_to_brand.py` - Extracts brand and product name from an image.
- `description.py` - Generates a product description based on brand and product name.
- `category1.py` - Determines the primary category of a product.
- `category2.py` - Determines the subcategory based on the primary category.
- `image_selector.py` - Fetches and selects the best image for a product using Google Custom Search API.
- `backgroundrm.py` - Removes the background from the selected image.
- `data.csv` - Stores processed product information.

## Installation
### Prerequisites
- Python 3.7+
- OpenAI API key
- Replicate API key
- Google Custom Search API key and CX ID
- Required Python packages (install via `requirements.txt` if provided)

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and set up API keys:
   ```bash
   OPENAI_API_KEY=<your-openai-api-key>
   REPLICATE_API_TOKEN=<your-replicate-api-token>
   GOOGLE_CUSTOM_SEARCH_API_KEY=<your-google-api-key>
   GOOGLE_CX_ID=<your-google-cx-id>
   ```

## Usage
To run the full pipeline with an image URL:
```bash
python main.py <image_url>
```

## Output
- Stores processed data in `data.csv`
- Saves best image selection in `best_images.csv`
- Stores processed images in the `processed_images/` directory

## License
This project is licensed under the MIT License.

## Author
Developed by Tomas Indriūnas.

