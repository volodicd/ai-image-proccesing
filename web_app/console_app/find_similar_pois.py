# find_similar_pois.py
from config import fetch_data_from_db


def find_similar_pois(city_id, place_id_or_name):
    if place_id_or_name.isdigit():
        # Input is a numeric ID
        query = """
        SELECT p.id, p.title, p.categories
        FROM points_of_interest p
        WHERE p.city_id = %s AND p.id = %s;
        """
        place = fetch_data_from_db(query, (city_id, place_id_or_name))
    else:
        # Input is a name
        query = """
        SELECT p.id, p.title, p.categories
        FROM points_of_interest p
        WHERE p.city_id = %s AND p.title = %s;
        """
        place = fetch_data_from_db(query, (city_id, place_id_or_name))

    if not place:
        print("No place found with the given ID or name.")
        return

    place = place[0]  # Assuming place_id_or_name is unique in the city
    categories = place['categories']

    if not categories or len(categories) < 5:
        print("The selected place does not have enough categories.")
        return

    # Find other places with at least five similar categories
    query = """
    SELECT p.id, p.title, p.description, p.image_url
    FROM points_of_interest p
    WHERE p.city_id = %s AND p.id != %s
    AND array_length(array(SELECT unnest(p.categories) INTERSECT SELECT unnest(%s)), 1) >= 5;
    """
    similar_places = fetch_data_from_db(query, (city_id, place['id'], categories))

    if similar_places:
        for sp in similar_places:
            print(f"Name: {sp['title']}")
            print(f"Description: {sp['description']}")
            print(f"Image URL: {sp['image_url']}")
            print("-" * 40)
    else:
        print("No similar places found in this city.")

    print("\n0. Back to main menu")
    choice = input("Enter your choice: ")
    if choice == "0":
        return
