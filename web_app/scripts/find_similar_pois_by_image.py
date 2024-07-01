# find_similar_pois_by_image.py
from sklearn.neighbors import NearestNeighbors
from console_app import  fetch_data_from_db

def find_similar_pois_by_image(city_id, place_id_or_name):


    query = """
    SELECT p.id, p.title, p.colours_rgb
    FROM points_of_interest p
    WHERE p.city_id = %s AND p.id = %s;
        """
    place = fetch_data_from_db(query, (city_id, place_id_or_name))


    if not place:

        return None

    place = place[0]  # Assuming place_id_or_name is unique in the city
    colours_rgb = place['colours_rgb']

    if not colours_rgb or len(colours_rgb) != 15:
        return None

    # Fetch all places with their colours_rgb data
    query = """
    SELECT p.id, p.title, p.description, p.image_url, p.colours_rgb
    FROM points_of_interest p
    WHERE p.city_id = %s AND p.colours_rgb IS NOT NULL AND array_length(p.colours_rgb, 1) = 15;
    """
    all_places = fetch_data_from_db(query, (city_id,))

    if not all_places:
        return None

    # Prepare data for KNN
    place_ids = [place['id'] for place in all_places]
    place_titles = [place['title'] for place in all_places]
    place_descriptions = [place['description'] for place in all_places]
    place_images = [place['image_url'] for place in all_places]
    place_colours = [place['colours_rgb'] for place in all_places]

    # Fit KNN model
    knn = NearestNeighbors(n_neighbors=5, algorithm='auto').fit(place_colours)
    distances, indices = knn.kneighbors([colours_rgb])

    similar_places_list = []

    for idx, index in enumerate(indices[0]):
        similar_places_dict = {
            'title': place_titles[index],
            'description': place_descriptions[index],
            'image_url': place_images[index]
        }
        similar_places_list.append(similar_places_dict)
    return similar_places_list

