# cities.py
from config import fetch_data_from_db
from display_places import display_places
from find_similar_pois import find_similar_pois
from find_similar_pois_by_image import find_similar_pois_by_image
from find_similar_pois_by_image_in_other_cities import find_similar_pois_by_image_in_other_cities


def display_cities():
    query = "SELECT id, name FROM cities ORDER BY name;"
    cities = fetch_data_from_db(query)
    if cities:
        print("Cities:")
        for city in cities:
            print(f"{city['id']}. {city['name']}")

        city_id = input("\nEnter the city ID to view details or 0 to go back to main menu: ")
        if city_id == "0":
            return

        while True:
            print("\n1. Display places of interest")
            print("2. Find similar places of interest in this city")
            print("3. Find similar places based on image similarity")
            print("4. Find similar places based on image similarity in other cities")
            print("5. Back to city selection")
            choice = input("Enter your choice: ")

            if choice == "1":
                display_places(city_id)
            elif choice == "2":
                place_id_or_name = input("Enter the place ID or name: ")
                find_similar_pois(city_id, place_id_or_name)
            elif choice == "3":
                place_id_or_name = input("Enter the place ID or name: ")
                find_similar_pois_by_image(city_id, place_id_or_name)
            elif choice == "4":
                place_id_or_name = input("Enter the place ID or name: ")
                find_similar_pois_by_image_in_other_cities(city_id, place_id_or_name)
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("No cities found.")

    print("\n0. Back to main menu")
    choice = input("Enter your choice: ")
    if choice == "0":
        return
