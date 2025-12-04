from db_connection import PostgresConnector
import psycopg2


def create_tables():
    """Crea tablas necesarias para la app: app_users y app_logs."""
    db = PostgresConnector()
    conn = db.connect()
    if conn is None:
        raise RuntimeError("No se pudo conectar a la base de datos")

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS app_logs (
            id SERIAL PRIMARY KEY,
            username TEXT,
            action TEXT,
            input_text TEXT,
            is_anomalous BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    conn.commit()
    cur.close()
    conn.close()


def log_action(username, action, input_text, is_anomalous=False):
    db = PostgresConnector()
    conn = db.connect()
    if conn is None:
        print("❌ No se pudo conectar para registrar log")
        return

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_logs (username, action, input_text, is_anomalous) VALUES (%s,%s,%s,%s)",
        (username, action, input_text, is_anomalous),
    )
    conn.commit()
    cur.close()
    conn.close()
