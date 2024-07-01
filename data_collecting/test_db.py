import json
import psycopg2

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

def fetch_data_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, poi.title, poi.description, poi.image_url, poi.categories, poi.colours_rgb
        FROM points_of_interest poi
        JOIN cities c ON poi.city_id = c.id
    """)
    rows = cursor.fetchall()

    data = {}
    for row in rows:
        city, title, description, image_url, categories, colours_rgb = row
        if city not in data:
            data[city] = []
        data[city].append({
            'title': title,
            'description': description,
            'image_url': image_url,
            'categories': categories,
            'colours_rgb': colours_rgb
        })

    cursor.close()
    return data

def write_data_to_json(data, output_file):
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data written to {output_file}")

def main():
    output_file = 'db_data.json'
    conn = connect_db()
    if conn:
        data = fetch_data_from_db(conn)
        write_data_to_json(data, output_file)
        conn.close()

if __name__ == "__main__":
    main()
