# 🛡️ Proyecto: Ciberseguridad Inteligente en Bases de Datos (IA + PostgreSQL)

Este proyecto analiza la actividad real de PostgreSQL y detecta:
- accesos sospechosos  
- consultas anómalas  
- comportamiento extraño  
mediante **Machine Learning (Isolation Forest)**.

La arquitectura es:

```
PostgreSQL → Extracción → Preprocesado → IA → Detección → Dashboard Web
```

---

# 🚀 1. Requisitos previos

- Python 3.8+
- PostgreSQL 12 o superior
- pgAdmin (opcional)
- pip

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# 🗄️ 2. CREACIÓN DE LA BASE DE DATOS (pgAdmin o Terminal)

El sistema se conecta a PostgreSQL usando:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "seguridad_db",
    "user": "seguser",
    "password": "segpass"
}
```

Por ello debes crear:

### ✔ Base de datos: `seguridad_db`  
### ✔ Usuario: `seguser`  
### ✔ Contraseña: `segpass`

---

# 🧩 2.1 Crear base de datos desde pgAdmin

1. En el panel izquierdo, clic derecho en **Databases**
2. Seleccionar **Create → Database**
3. En la ventana:

| Campo | Valor |
|-------|--------|
| Database | **seguridad_db** |
| Owner | postgres (por defecto) |

No llenar más campos.

Pulsar **Save**.

---

# 🔐 2.2 Crear usuario PostgreSQL (pgAdmin)

1. Clic derecho en **Login/Group Roles**
2. **Create → Login/Group Role**
3. Completar así:

### Pestaña "General"
| Campo | Valor |
|-------|--------|
| Name | **seguser** |

### Pestaña "Definition"
| Campo | Valor |
|-------|--------|
| Password | **segpass** |

### Pestaña "Privileges"
✔ Can Login  
✔ Create DB (opcional)
Guardar.
---
# 🎁 2.3 Dar permisos al usuario
Abrir **Query Tool** desde la base `seguridad_db`:
Ejecutar:
```sql
GRANT ALL PRIVILEGES ON DATABASE seguridad_db TO seguser;
```
---
# 📡 3. Probar la conexión a PostgreSQL

Ejecutar:

```bash
python src/user_extractor.py
```
# 🛡️ Proyecto: Ciberseguridad Inteligente en Bases de Datos (IA + PostgreSQL)

Este proyecto analiza la actividad real de PostgreSQL y detecta:
- accesos sospechosos
- consultas anómalas
- comportamiento extraño

Mediante Machine Learning (TF‑IDF + IsolationForest) se identifican outliers en las consultas y se muestran en un dashboard web.

---

## 1) Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

---

## 2) Configuración de la base de datos

Edita `src/config.py` para ajustar `DB_CONFIG` si tus credenciales/datos son diferentes.

Ejemplo (por defecto):

```python
DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "dbname": "seguridad_db",
        "user": "seguser",
        "password": "segpass"
}

MODEL_PATH = "data/modelo_entrenado.pkl"
VECTORIZER_PATH = "data/vectorizer.pkl"
```

### 2.1 Crear base y usuario (psql / pgAdmin)

Conéctate como superusuario y ejecuta:

```sql
CREATE DATABASE seguridad_db;
CREATE ROLE seguser WITH LOGIN PASSWORD 'segpass';
GRANT CONNECT ON DATABASE seguridad_db TO seguser;
GRANT USAGE, CREATE ON SCHEMA public TO seguser;

\c seguridad_db
CREATE TABLE IF NOT EXISTS app_users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_logs (
    id SERIAL PRIMARY KEY,
    username TEXT,
    action TEXT,
    input_text TEXT,
    is_anomalous BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Si no tienes permisos de superusuario, pide al DBA que ejecute los `GRANT` o que cree las tablas.

---

## 3) Inicializar tablas desde la web

Arranca la app web y usa el enlace `Iniciar / Crear tablas en la base de datos`.

```powershell
cd web
python app.py
```

> Nota: `seguser` necesita `CREATE` en `public` para que `/init_db` funcione.

---

## 4) Ejecutar la web

```powershell
cd web
python app.py
```

Abrir: http://127.0.0.1:5000/

### Endpoints disponibles

- `/` — Dashboard principal (muestra `pid`, `usename`, `client_addr`, `state`, `query_start`, `log`, `anomaly`).
- `/init_db` — Crear tablas `app_users` y `app_logs` (GET).
- `/create_user` — Crear usuario (POST, formulario en la web).
- `/login_check` — Verificar credenciales (POST, formulario en la web).
- `/test_input` — Enviar texto de prueba (POST) para detección por reglas.
- `/save_detections` — Guardar detecciones actuales en `app_logs` (POST).
- `/logs` — Ver tabla `app_logs` (GET).
- `/train` — Re-entrenar vectorizer + modelo (POST).

---

## 5) Entrenamiento y persistencia

- `data/vectorizer.pkl` — TF‑IDF vectorizer guardado (controlado por `src/log_preprocessor.py`).
- `data/modelo_entrenado.pkl` — Modelo IsolationForest guardado (`src/anomaly_model.py`).

Puedes entrenar desde la web con el botón C (ruta `/train`) o ejecutar tu propio script de entrenamiento (si lo añades).

---

## 6) Guardar y consultar detecciones

- Pulsa **A) Guardar detecciones** para insertar lo que el modelo ha analizado en `app_logs`.
- Accede a `/logs` para ver el historial. Ejemplos SQL:

```sql
SELECT * FROM app_logs ORDER BY created_at DESC LIMIT 200;
SELECT * FROM app_logs WHERE is_anomalous = true ORDER BY created_at DESC;
```

Si quieres que `app_logs` guarde solo anomalías, puedo cambiar `/save_detections` para filtrar `anomaly == -1`.

---

## 7) Notas

- Este es un proyecto de prueba con `config.py` compartido para todos los usuarios.
- Las credenciales están en `src/config.py` para facilitar la colaboración.

---

## 8) Troubleshooting rápido

- `CREATE TABLE` falla por permisos: conéctate como superusuario y ejecuta `GRANT USAGE, CREATE ON SCHEMA public TO seguser;`.
- Error `ValueError: X has N features, but IsolationForest is expecting M`: vectorizer y modelo desincronizados. Soluciones:
    - Ejecutar `/train` para re-entrenar y sincronizar.
    - Eliminar `data/modelo_entrenado.pkl` y `data/vectorizer.pkl` y re-entrenar.

Comandos útiles:

```powershell
# Ver sesiones activas (lo que lee la app)
psql -h localhost -U seguser -d seguridad_db -c "SELECT pid, usename, client_addr, state, query, query_start FROM pg_stat_activity;"

# Ver logs guardados por la web
psql -h localhost -U seguser -d seguridad_db -c "SELECT * FROM app_logs ORDER BY created_at DESC LIMIT 100;"
```

---

## 9) Recomendaciones para entrega / informe

- Documenta el flujo: extracción (pg_stat_activity) → TF‑IDF → IsolationForest → dashboard.
- Muestra ejemplos y explica limitaciones.
- Incluye pasos reproducibles: crear BD, `init_db`, crear usuario, `train`, `save_detections`, `logs`.

