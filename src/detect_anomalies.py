from user_extractor import UserExtractor
from log_preprocessor import LogPreprocessor
from anomaly_model import AnomalyModel
from config import MODEL_PATH, VECTORIZER_PATH
import pandas as pd
from pathlib import Path
import traceback
from rule_detector import detect_by_rules

def detectar_anomalias():
	"""Extrae sesiones, preprocesa logs, ejecuta el modelo y devuelve un DataFrame
	con la columna `anomaly` (predicción del modelo).
	"""
	print("Extrayendo sesiones activas...")
	extractor = UserExtractor()
	logs_df = extractor.get_active_sessions()

	logs = logs_df["query"].fillna("").tolist()

	print("Procesando logs (TF-IDF)...")
	pre = LogPreprocessor()

	model_exists = Path(MODEL_PATH).exists()
	vectorizer_exists = Path(VECTORIZER_PATH).exists()

	if vectorizer_exists:
		try:
			pre.load(VECTORIZER_PATH)
			X = pre.transform(logs)
		except Exception as e:
			print("Error cargando vectorizer, volveré a ajustar:", e)
			traceback.print_exc()
			X = pre.fit_transform(logs)
			# guarda nuevo vectorizer
			pre.save(VECTORIZER_PATH)
	else:
		X = pre.fit_transform(logs)
		try:
			pre.save(VECTORIZER_PATH)
		except Exception as e:
			print("No pude guardar vectorizer:", e)

	print("Cargando modelo y detectando anomalías...")
	model = AnomalyModel()
	try:
		preds = model.predict(X)
	except ValueError as e:
		print("Incompatibilidad de features entre modelo y vectorizer:", e)
		traceback.print_exc()
		# re-entrenar con X y volver a predecir
		print("Re-entrenando modelo con el vectorizer actual para mantener consistencia...")
		model.train(X)
		preds = model.predict(X)

	logs_df["ml_anomaly"] = preds ==-1
	rule_anoms = []
	rules_triggered = []

	print("Aplicando reglas SQL...")

	for log in logs:
		is_rule_anom, rules = detect_by_rules(log)
		rule_anoms.append(is_rule_anom)
		rules_triggered.append(", ".join(r["name"] for r in rules))


	logs_df["rule_anomaly"] = rule_anoms
	logs_df["rules_triggered"] = rules_triggered
	#Decisión final híbrida
	logs_df["anomaly"] = (logs_df["ml_anomaly"] | logs_df["rule_anomaly"]).map(
        {True: -1, False: 1}
    )
	# Normaliza el nombre de columna para la plantilla web (index.html espera 'log')
	if "log" not in logs_df.columns and "query" in logs_df.columns:
		logs_df["log"] = logs_df["query"].astype(str)

	print("Resultados finales:")
	print(logs_df[
            ["log", "ml_anomaly", "rule_anomaly", "rules_triggered", "anomaly"]
        ].head())

	return logs_df


if __name__ == "__main__":
	detectar_anomalias()
