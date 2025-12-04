from user_extractor import UserExtractor
from log_preprocessor import LogPreprocessor
from anomaly_model import AnomalyModel
import pandas as pd

# Extraemos logs reales
print("📡 Extrayendo logs de PostgreSQL...")
extractor = UserExtractor()
logs_df = extractor.get_active_sessions()

logs = logs_df["query"].fillna("").tolist()

# Preprocesamos logs
print("🧹 Procesando logs...")
pre = LogPreprocessor()
X = pre.fit_transform(logs)

# Entrenamos modelo
print("🤖 Entrenando modelo...")
model = AnomalyModel()
model.train(X)

print("✅ Entrenamiento completado.")
