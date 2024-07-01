# config.py
import psycopg2

# Database configuration
db_config = {
    "host": "localhost",
    "database": "tech_project",
    "user": "postgres",
    "password": "12345678",
    "port": 6543
}

def connect_db():
    return psycopg2.connect(**db_config)
