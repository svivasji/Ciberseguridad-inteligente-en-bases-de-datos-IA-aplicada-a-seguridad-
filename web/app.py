from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import os

# Permitir importar desde src/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from detect_anomalies import detectar_anomalias  # tu función real
from auth import create_user, check_login
from db_setup import create_tables, log_action
from db_connection import PostgresConnector
import psycopg2
from flask import jsonify
from user_extractor import UserExtractor
from log_preprocessor import LogPreprocessor
from anomaly_model import AnomalyModel
from config import VECTORIZER_PATH, MODEL_PATH

app = Flask(__name__)
app.secret_key = "dev-secret"  # cambiar en producción


@app.route("/")
def home():
    df = detectar_anomalias()  # obtiene logs + anomalías en vivo
    anomalies = df[df["anomaly"] == -1]

    return render_template(
        "index.html",
        total=len(df),
        anomal=len(anomalies),
        table=df.to_dict(orient="records")
    )


@app.route("/init_db")
def init_db():
    try:
        create_tables()
        flash("Tablas creadas correctamente.", "success")
    except Exception as e:
        flash(f"Error creando tablas: {e}", "danger")
    return redirect(url_for("home"))


@app.route("/create_user", methods=["POST"])
def route_create_user():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        flash("Usuario y contraseña son requeridos.", "warning")
        return redirect(url_for("home"))

    ok, msg = create_user(username, password)
    if ok:
        log_action(username, "create_user", "--", False)
        flash(msg or "Usuario creado correctamente.", "success")
    else:
        flash(msg or "No se pudo crear el usuario (revisar logs).", "danger")
    return redirect(url_for("home"))


@app.route("/login_check", methods=["POST"])
def route_login_check():
    username = request.form.get("login_user")
    password = request.form.get("login_pass")
    if not username or not password:
        flash("Usuario y contraseña son requeridos para login.", "warning")
        return redirect(url_for("home"))

    ok = check_login(username, password)
    log_action(username, "login_attempt", "--", not ok)
    if ok:
        flash("Login correcto.", "success")
    else:
        flash("Credenciales incorrectas.", "danger")
    return redirect(url_for("home"))


@app.route("/test_input", methods=["POST"])
def route_test_input():
    username = request.form.get("tester_user") or "anonymous"
    user_input = request.form.get("user_input") or ""

    # Detección básica de patrones sospechosos (no ejecutar SQL crudo)
    suspicious_tokens = [";", "--", "/*", "*/", " OR ", " AND ", "DROP ", "UNION "]
    is_suspicious = any(tok.upper() in user_input.upper() for tok in suspicious_tokens)
    log_action(username, "test_input", user_input, is_suspicious)

    if is_suspicious:
        flash("Entrada marcada como sospechosa (posible inyección).", "warning")
    else:
        flash("Entrada parece limpia según reglas básicas.", "info")
    return redirect(url_for("home"))


@app.route('/save_detections', methods=['POST'])
def save_detections():
    try:
        df = detectar_anomalias()
        # Guardar sólo las filas marcadas como anómalas (anomaly == -1)
        anom_df = df[df['anomaly'] == -1]
        count = 0
        for _, row in anom_df.iterrows():
            username = row.get('usename') or 'system'
            action = 'model_detection'
            input_text = str(row.get('log') or row.get('query') or '')
            is_anom = True
            log_action(username, action, input_text, is_anom)
            count += 1
        flash(f"Guardadas {count} detecciones anómalas en app_logs.", "success")
    except Exception as e:
        flash(f"Error guardando detecciones: {e}", "danger")
    return redirect(url_for('home'))


@app.route('/logs')
def view_logs():
    db = PostgresConnector()
    conn = db.connect()
    rows = []
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, username, action, input_text, is_anomalous, created_at FROM app_logs ORDER BY created_at DESC LIMIT 500")
            cols = [d[0] for d in cur.description]
            for r in cur.fetchall():
                rows.append(dict(zip(cols, r)))
        except Exception as e:
            flash(f"Error leyendo app_logs: {e}", "danger")
        cur.close()
        conn.close()
    else:
        flash("No hay conexión a la BD para leer logs.", "warning")
    return render_template('logs.html', rows=rows)


@app.route('/users')
def view_users():
    db = PostgresConnector()
    conn = db.connect()
    users = []
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, username, created_at FROM app_users ORDER BY created_at DESC LIMIT 500")
            cols = [d[0] for d in cur.description]
            for r in cur.fetchall():
                users.append(dict(zip(cols, r)))
        except Exception as e:
            flash(f"Error leyendo app_users: {e}", "danger")
        cur.close()
        conn.close()
    else:
        flash("No hay conexión a la BD para leer usuarios.", "warning")
    return render_template('users.html', users=users)


@app.route('/train', methods=['POST'])
def train_model():
    try:
        # Obtener logs y entrenar vectorizer + modelo explícitamente
        extractor = UserExtractor()
        logs_df = extractor.get_active_sessions()
        logs = logs_df['query'].fillna('').tolist()

        pre = LogPreprocessor()
        X = pre.fit_transform(logs)
        try:
            pre.save(VECTORIZER_PATH)
        except Exception:
            pass

        model = AnomalyModel()
        model.train(X)
        flash('Entrenamiento completo y modelo guardado.', 'success')
    except Exception as e:
        flash(f'Error entrenando modelo: {e}', 'danger')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
