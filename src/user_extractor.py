import pandas as pd
from db_connection import PostgresConnector

class UserExtractor:

    def __init__(self):
        self.db = PostgresConnector()

    def get_active_sessions(self):
        """
        Devuelve los logs reales del sistema PostgreSQL, incluyendo:
        - query ejecutada
        - usuario
        - ip
        - timestamp
        - estado
        """
        query = """
            SELECT pid, usename, client_addr, state, query, query_start
            FROM pg_stat_activity;
        """
        conn = self.db.connect()
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def get_users(self):
        """
        Devuelve los usuarios reales registrados en PostgreSQL.
        """
        query = "SELECT usename, usecreatedb, usesuper, valuntil FROM pg_user;"
        conn = self.db.connect()
        df = pd.read_sql(query, conn)
        conn.close()
        return df
