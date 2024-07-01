import json
import aiohttp
import asyncio
import psycopg2
from tqdm import tqdm

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


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS points_of_interest (
        id SERIAL PRIMARY KEY,
        city_id INTEGER REFERENCES cities(id),
        title VARCHAR(255),
        description TEXT,
        image_url TEXT,
        categories TEXT[],
        colours_rgb INTEGER[]
    );
    """)
    conn.commit()
    cursor.close()


# Define the cities and their coordinates
cities = {
    "Berlin": [(52.5200, 13.4050), (52.5400, 13.4050)],
    "Stockholm": [(59.3293, 18.0686), (59.3493, 18.0686)],
    "Klaipeda": [(55.7033, 21.1443)],
    "Tokyo": [(35.6895, 139.6917), (35.7095, 139.7317)]
}


# Function to fetch places of interest for a given city
async def fetch_places_of_interest(session, city, coordinates):
    places = []
    for lat, lon in coordinates:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=geosearch&gsradius=10000&gscoord={lat}|{lon}&gslimit=500"
        async with session.get(url) as response:
            data = await response.json()
            if 'query' in data and 'geosearch' in data['query']:
                for item in data['query']['geosearch']:
                    place = {
                        'city': city,
                        'title': item.get('title', 'Unknown'),
                        'lat': item.get('lat', 0.0),
                        'lon': item.get('lon', 0.0),
                        'type': 'Unknown',  # Placeholder for POI type
                        'description': 'Unknown'  # Placeholder for description
                    }
                    places.append(place)
    return places


# Function to fetch additional details of a POI
async def fetch_poi_details(session, place):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={place['title']}&prop=pageimages|extracts|categories&exintro&explaintext&format=json&pithumbsize=500"
    try:
        async with session.get(url) as response:
            data = await response.json()
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                if 'extract' in page_info:
                    place['description'] = page_info['extract'].split('.')[0] + '.'  # Take the first sentence
                if 'categories' in page_info:
                    place['categories'] = [category['title'] for category in page_info['categories']]
                if 'thumbnail' in page_info:
                    place['image_url'] = page_info['thumbnail']['source']
            return place
    except Exception as e:
        print(f"Error fetching details for {place['title']}: {e}")
        return place


# Function to merge duplicate POIs
def merge_duplicate_pois(places):
    unique_places = {}
    for place in places:
        title = place['title']
        if title in unique_places:
            # Merge categories
            existing_categories = unique_places[title].get('categories', [])
            new_categories = place.get('categories', [])
            unique_places[title]['categories'] = list(set(existing_categories + new_categories))
            # Merge descriptions (concatenate if different)
            if unique_places[title]['description'] != place['description']:
                unique_places[title]['description'] += " " + place['description']
        else:
            # Initialize categories if not present
            if 'categories' not in place:
                place['categories'] = []
            unique_places[title] = place
    return list(unique_places.values())


# Function to insert data into the database
def insert_data_into_db(conn, city, places):
    cursor = conn.cursor()

    # Check if the city already exists
    cursor.execute("SELECT id FROM cities WHERE name = %s;", (city,))
    result = cursor.fetchone()
    if result:
        city_id = result[0]
    else:
        cursor.execute("INSERT INTO cities (name) VALUES (%s) RETURNING id;", (city,))
        city_id = cursor.fetchone()[0]

    for place in places:
        title = place.get('title')
        description = place.get('description')
        image_url = place.get('image_url')
        categories = place.get('categories', [])
        colours_rgb = place.get('colours_rgb', [])
        cursor.execute("""
            INSERT INTO points_of_interest 
            (city_id, title, description, image_url, categories, colours_rgb) 
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (city_id, title, description, image_url, categories, colours_rgb))

    conn.commit()
    cursor.close()


# Main function
async def main():
    conn = connect_db()
    if conn is None:
        print("Exiting script due to failed database connection.")
        return

    # Create tables if they don't exist
    create_tables(conn)

    async with aiohttp.ClientSession() as session:
        # Iterate through each city
        for city, coordinates in cities.items():
            print(f"Fetching data for {city}...")
            places = await fetch_places_of_interest(session, city, coordinates)
            # Fetch additional details for each place
            tasks = [fetch_poi_details(session, place) for place in places]
            places_with_details = await asyncio.gather(*tasks)
            # Deduplicate places
            unique_places = merge_duplicate_pois(places_with_details)
            # Insert data into the database
            insert_data_into_db(conn, city, unique_places)
            print(f"Completed data upload for {city}")

    conn.close()
    print("Data upload completed.")


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
