from db_connection import PostgresConnector
from werkzeug.security import generate_password_hash, check_password_hash
from db_setup import create_tables
import psycopg2


def create_user(username: str, password: str):
    """
    Crea un usuario. Retorna (ok: bool, message: str).
    """
    if not username or not password:
        return False, "Usuario o contraseña vacíos"

    username = username.strip()

    db = PostgresConnector()
    conn = db.connect()
    if conn is None:
        return False, "No se pudo conectar a la base de datos"

    cur = conn.cursor()
    pwd_hash = generate_password_hash(password)

    try:
        # comprobar existencia
        cur.execute("SELECT 1 FROM app_users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "El usuario ya existe"

        cur.execute(
            "INSERT INTO app_users (username, password_hash) VALUES (%s, %s)",
            (username, pwd_hash),
        )
        conn.commit()
    except Exception as e:
        # Si la tabla no existe, crearla y reintentar una vez
        print("⚠️ Exception en create_user:", e)
        if isinstance(e, psycopg2.errors.UndefinedTable):
            try:
                create_tables()
                cur.execute(
                    "INSERT INTO app_users (username, password_hash) VALUES (%s, %s)",
                    (username, pwd_hash),
                )
                conn.commit()
            except Exception as e2:
                conn.rollback()
                cur.close()
                conn.close()
                print("⚠️ Error creando usuario tras crear tablas:", e2)
                return False, f"Error creando usuario: {e2}"
        else:
            conn.rollback()
            cur.close()
            conn.close()
            print("⚠️ Error creando usuario:", e)
            return False, f"Error creando usuario: {e}"

    cur.close()
    conn.close()
    return True, "Usuario creado correctamente"


def check_login(username: str, password: str) -> bool:
    db = PostgresConnector()
    conn = db.connect()
    if conn is None:
        return False

    cur = conn.cursor()
    try:
        cur.execute("SELECT password_hash FROM app_users WHERE username = %s", (username,))
        row = cur.fetchone()
    except Exception as e:
        # Si la tabla falta, crearla y devolver False (no hay usuarios todavía)
        if isinstance(e, psycopg2.errors.UndefinedTable):
            try:
                create_tables()
            except Exception as ce:
                print("⚠️ Error creando tablas en check_login:", ce)
            cur.close()
            conn.close()
            return False
        else:
            cur.close()
            conn.close()
            print("⚠️ Error en check_login:", e)
            return False

    cur.close()
    conn.close()

    if not row:
        return False

    pwd_hash = row[0]
    return check_password_hash(pwd_hash, password)
