# find_similar_pois_by_image.py
import numpy as np
from sklearn.neighbors import NearestNeighbors
from config import fetch_data_from_db


def find_similar_pois_by_image(city_id, place_id_or_name):
    if place_id_or_name.isdigit():
        # Input is a numeric ID
        query = """
        SELECT p.id, p.title, p.colours_rgb
        FROM points_of_interest p
        WHERE p.city_id = %s AND p.id = %s;
        """
        place = fetch_data_from_db(query, (city_id, place_id_or_name))
    else:
        # Input is a name
        query = """
        SELECT p.id, p.title, p.colours_rgb
        FROM points_of_interest p
        WHERE p.city_id = %s AND p.title = %s;
        """
        place = fetch_data_from_db(query, (city_id, place_id_or_name))

    if not place:
        print("No place found with the given ID or name.")
        return

    place = place[0]  # Assuming place_id_or_name is unique in the city
    colours_rgb = place['colours_rgb']

    if not colours_rgb or len(colours_rgb) != 15:
        print("Invalid input, choose another place.")
        return

    # Fetch all places with their colours_rgb data
    query = """
    SELECT p.id, p.title, p.description, p.image_url, p.colours_rgb
    FROM points_of_interest p
    WHERE p.city_id = %s AND p.colours_rgb IS NOT NULL AND array_length(p.colours_rgb, 1) = 15;
    """
    all_places = fetch_data_from_db(query, (city_id,))

    if not all_places:
        print("No other places with valid colour RGB data found in this city.")
        return

    # Prepare data for KNN
    place_ids = [place['id'] for place in all_places]
    place_titles = [place['title'] for place in all_places]
    place_descriptions = [place['description'] for place in all_places]
    place_images = [place['image_url'] for place in all_places]
    place_colours = [place['colours_rgb'] for place in all_places]

    # Fit KNN model
    knn = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(place_colours)
    distances, indices = knn.kneighbors([colours_rgb])

    print(f"Selected place: {place['title']}\n")
    print("5 most similar places based on image similarity:")
    for index in indices[0]:
        print(f"Name: {place_titles[index]}")
        print(f"Description: {place_descriptions[index]}")
        print(f"Image URL: {place_images[index]}")
        print("-" * 40)

    print("\n0. Back to main menu")
    choice = input("Enter your choice: ")
    if choice == "0":
        return
