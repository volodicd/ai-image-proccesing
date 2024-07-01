# config.py
import psycopg2
from psycopg2.extras import RealDictCursor

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
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None

def fetch_data_from_db(query, params=None):
    conn = connect_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
