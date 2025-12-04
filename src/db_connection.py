import psycopg2
from config import DB_CONFIG

class PostgresConnector:
    def connect(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            print("❌ Error conectando a PostgreSQL:", e)
            return None
