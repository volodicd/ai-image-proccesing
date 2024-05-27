import json
import requests
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from tqdm import tqdm


# Function to download and convert .jpg to .png using Pillow
def download_convert_jpg_to_png(url):
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        if img.format in ['JPEG', 'JPG']:
            img = img.convert('RGB')
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            img = Image.open(img_bytes)
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except requests.exceptions.RequestException as e:
        print(f"Network error downloading image from {url}: {e}")
        return None
    except UnidentifiedImageError:
        print(f"Error: Cannot identify image file from {url}")
        return None
    except Exception as e:
        print(f"Error downloading or converting image from {url}: {e}")
        return None


# Function to download and decode .png image using Pillow
def download_png_image(url):
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except requests.exceptions.RequestException as e:
        print(f"Network error downloading image from {url}: {e}")
        return None
    except UnidentifiedImageError:
        print(f"Error: Cannot identify image file from {url}")
        return None
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


# Function to download image and choose the appropriate method
def download_image(url):
    if url.lower().endswith('.jpg') or url.lower().endswith('.jpeg'):
        return download_convert_jpg_to_png(url)
    elif url.lower().endswith('.png'):
        return download_png_image(url)
    else:
        print(f"Unsupported image format for URL: {url}")
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

        # Format the feature vector
        feature_vector = []
        for idx in sorted_indices:
            feature_vector.extend(kmeans.cluster_centers_[idx])

        return np.array(feature_vector).astype(int).tolist()  # Convert to list for JSON serialization
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


# Function to process all images and save feature vectors
def process_images(images_data, output_file, k=5):
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

    # Filter out images without valid colours_RGB
    filtered_data = {city: [img for img in images if img['colours_RGB']] for city, images in images_data.items()}

    # Save results to a JSON file
    with open(output_file, 'w') as file:
        json.dump(filtered_data, file, indent=4)
    print(f"Feature vectors saved to {output_file}")
    print(f"Total number of processed elements with 'colours_RGB' data: {total_processed}")
    print(f"Total number of images processed: {total_images}")
    print(f"Total number of images with valid colours_RGB: {total_processed}")


# Main function
def main():
    input_file = 'images_data.json'
    output_file = 'processed_images_data.json'

    # Load image data from the JSON file created in Task 1
    with open(input_file, 'r') as file:
        images_data = json.load(file)

    # Process images and save feature vectors
    process_images(images_data, output_file)


# Execute main function
if __name__ == "__main__":
    main()
