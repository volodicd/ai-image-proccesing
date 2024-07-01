import json
import requests
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm
import os
import time
import psycopg2
from psycopg2.extras import Json

# Custom User-Agent for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Temporary directory for storing downloaded images
TEMP_DIR = 'temp_images'

# Create the temporary directory if it does not exist
os.makedirs(TEMP_DIR, exist_ok=True)

# Database configuration
db_config = {
    "host": "localhost",
    "database": "tech_project",
    "user": "postgres",
    "password": "12345678",
    "port": 5432
}

def connect_db():
    try:
        conn = psycopg2.connect(**db_config)
        print("Connection to database established successfully.")
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None

# Function to download and save image to disk
def download_image(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            # Create a temporary file path
            img_path = os.path.join(TEMP_DIR, os.path.basename(url))
            with open(img_path, 'wb') as f:
                f.write(response.content)

            # Open the image using Pillow
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return img
        except requests.exceptions.RequestException as e:
            print(f"Network error downloading image from {url}: {e}, attempt {attempt + 1} of {max_retries}")
            time.sleep(1)  # Wait for 1 second before retrying
        except UnidentifiedImageError:
            print(f"Error: Cannot identify image file from {url}, attempt {attempt + 1} of {max_retries}")
            return None
        except Exception as e:
            print(f"Error downloading image from {url}: {e}, attempt {attempt + 1} of {max_retries}")
            return None
    return None

# Function to apply K-means and extract dominant colors
def extract_dominant_colors(image, k=5):
    try:
        # Calculate new dimensions while keeping aspect ratio
        width, height = image.size
        if width > height:
            new_width = 100
            new_height = int((height / width) * 100)
        else:
            new_height = 100
            new_width = int((width / height) * 100)

        image = image.resize((new_width, new_height))
        data = np.array(image)
        data = data.reshape((-1, 3))

        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(data)

        # Sort clusters by the number of points in each cluster
        unique, counts = np.unique(kmeans.labels_, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1]  # Sort in descending order

        # Format the feature vector and convert to integers
        feature_vector = []
        for idx in sorted_indices:
            feature_vector.extend([int(x) for x in kmeans.cluster_centers_[idx]])

        print(f"Extracted colors: {feature_vector}")  # Debug print
        return feature_vector  # Return as a list of integers
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# Function to process all images and save feature vectors
def process_images(conn, k=5):
    cursor = conn.cursor()

    # Fetch images data from the database
    cursor.execute("""
        SELECT c.name, poi.id, poi.title, poi.image_url, poi.description, poi.categories
        FROM points_of_interest poi
        JOIN cities c ON poi.city_id = c.id
        WHERE poi.image_url IS NOT NULL;
    """)
    rows = cursor.fetchall()

    images_data = {}
    for row in rows:
        city, poi_id, title, image_url, description, categories = row
        if city not in images_data:
            images_data[city] = []
        images_data[city].append({
            'id': poi_id,
            'title': title,
            'image_url': image_url,
            'description': description,
            'categories': categories,
            'colours_RGB': []
        })

    total_processed = 0
    total_images = sum(len(images) for images in images_data.values())

    for city, images in images_data.items():
        print(f"Processing images for {city}...")
        for image_info in tqdm(images, desc=f"Processing {city}", unit="image"):
            image_url = image_info['image_url']
            image = download_image(image_url)
            if image:
                feature_vector = extract_dominant_colors(image, k)
                if feature_vector is not None:
                    image_info['colours_RGB'] = feature_vector
                    total_processed += 1
                else:
                    image_info['colours_RGB'] = None
            else:
                image_info['colours_RGB'] = None

        print(f"Completed processing images for {city}")

    # Update the database with the processed data
    for city, images in images_data.items():
        for image_info in images:
            print(f"Updating database for ID {image_info['id']} with colours_RGB: {image_info['colours_RGB']}")  # Debug print
            cursor.execute("""
                UPDATE points_of_interest
                SET colours_rgb = %s
                WHERE id = %s;
            """, (image_info['colours_RGB'], image_info['id']))
        conn.commit()

    print(f"Total number of processed elements with 'colours_RGB' data: {total_processed}")
    print(f"Total number of images processed: {total_images}")
    print(f"Total number of images with valid colours_RGB: {total_processed}")

    cursor.close()

    # Cleanup: remove temporary images
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting temporary file {file_path}: {e}")

# Main function
def main():
    conn = connect_db()
    if conn:
        process_images(conn)
        conn.close()

# Execute main function
if __name__ == "__main__":
    main()
