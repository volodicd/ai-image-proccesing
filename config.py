import json
import psycopg2
from psycopg2 import sql

# Database configuration
db_config = {
    "host": "localhost",
    "database": "tech_project",
    "user": "postgres",
    "password": "qwerty"  # Replace with a secure password (avoid storing in plain text)
}

# Function to insert data into the database
def insert_data(city, data):
    try:
        # Connect to the database
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()

        # Insert city data
        cursor.execute("INSERT INTO city (name) VALUES (%s) RETURNING city_id;", (city,))
        city_id = cursor.fetchone()[0]

        # Insert places and categories
        for place in data:
            cursor.execute("""
                INSERT INTO place (name, description, lat, lon, city_id) VALUES (%s, %s, %s, %s, %s) RETURNING place_id;
            """, (place['title'], place['description'], place['lat'], place['lon'], city_id))
            place_id = cursor.fetchone()[0]

            # Assuming POI type is treated as category
            cursor.execute("""
                INSERT INTO category (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;
            """, (place['type'],))
            category_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO place_category (place_id, category_id) VALUES (%s, %s);
            """, (place_id, category_id))

            # Insert image URL
            cursor.execute("""
                INSERT INTO place_image (place_id, image_url) VALUES (%s, %s);
            """, (place_id, place['image_url']))

        # Commit the transaction
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print(f"Error inserting data into PostgreSQL table: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Main function to load data and insert into the database
def main():
    # Load the images data
    with open('images_data.json', 'r') as file:
        images_data = json.load(file)

    # Insert data for each city
    for city, data in images_data.items():
        insert_data(city, data)

if __name__ == "__main__":
    main()
