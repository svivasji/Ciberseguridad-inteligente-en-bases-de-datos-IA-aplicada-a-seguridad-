import psycopg2
import pandas as pd
from config import DB_CONFIG

class PostgresConnector:
    def connect(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            print("Error conectando a PostgreSQL:", e)
            return None
    def get_logs_dataframe(self):
        conn = self.connect()
        query = """
            SELECT created_at, username, is_anomalous
            FROM app_logs
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
