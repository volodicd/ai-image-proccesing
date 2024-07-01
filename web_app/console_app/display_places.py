# display_places.py
from config import fetch_data_from_db


def display_places(city_id):
    query = """
    SELECT p.id, p.title, p.description, p.image_url
    FROM points_of_interest p
    WHERE p.city_id = %s
    ORDER BY p.id DESC;
    """
    places = fetch_data_from_db(query, (city_id,))
    if places:
        for place in places:
            print(f"Name: {place['title']}")
            print(f"Description: {place['description']}")
            print(f"Image URL: {place['image_url']}")
            print("-" * 40)
    else:
        print("No places of interest found in this city.")

    print("\n0. Back to main menu")
    choice = input("Enter your choice: ")
    if choice == "0":
        return
