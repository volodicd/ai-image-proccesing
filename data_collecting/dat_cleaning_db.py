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


def delete_empty_entries(conn):
    cursor = conn.cursor()
    try:
        # Delete entries where colours_rgb is empty
        cursor.execute("""
            DELETE FROM points_of_interest
            WHERE colours_rgb IS NULL OR array_length(colours_rgb, 1) = 0;
        """)

        # Delete entries where categories is empty
        cursor.execute("""
            DELETE FROM points_of_interest
            WHERE categories IS NULL OR array_length(categories, 1) = 0;
        """)

        conn.commit()
        print("Entries with empty colours_rgb or categories have been deleted.")
    except Exception as e:
        print(f"Error deleting entries: {e}")
        conn.rollback()
    finally:
        cursor.close()


def main():
    conn = connect_db()
    if conn:
        delete_empty_entries(conn)
        conn.close()


if __name__ == "__main__":
    main()
