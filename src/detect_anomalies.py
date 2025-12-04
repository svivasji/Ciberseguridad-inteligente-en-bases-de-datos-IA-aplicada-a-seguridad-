from user_extractor import UserExtractor
from log_preprocessor import LogPreprocessor
from anomaly_model import AnomalyModel
from config import MODEL_PATH, VECTORIZER_PATH
import pandas as pd
from pathlib import Path
import traceback


def detectar_anomalias():
	"""Extrae sesiones, preprocesa logs, ejecuta el modelo y devuelve un DataFrame
	con la columna `anomaly` (predicción del modelo).
	"""
	print("📡 Extrayendo sesiones activas...")
	extractor = UserExtractor()
	logs_df = extractor.get_active_sessions()

	logs = logs_df["query"].fillna("").tolist()

	print("🧹 Procesando logs (TF-IDF)...")
	pre = LogPreprocessor()

	model_exists = Path(MODEL_PATH).exists()
	vectorizer_exists = Path(VECTORIZER_PATH).exists()

	# Preferir usar vectorizer guardado si existe (mantiene consistencia de features)
	if vectorizer_exists:
		try:
			pre.load(VECTORIZER_PATH)
			X = pre.transform(logs)
		except Exception as e:
			print("⚠️ Error cargando vectorizer, volveré a ajustar:", e)
			traceback.print_exc()
			X = pre.fit_transform(logs)
			# guardar nuevo vectorizer
			pre.save(VECTORIZER_PATH)
	else:
		# no hay vectorizer guardado: ajustar y guardar
		X = pre.fit_transform(logs)
		try:
			pre.save(VECTORIZER_PATH)
		except Exception as e:
			print("⚠️ No pude guardar vectorizer:", e)

	print("🤖 Cargando modelo y detectando anomalías...")
	model = AnomalyModel()

	# Si el modelo existe pero el vectorizer fue recién ajustado y tiene distinta dimensión,
	# puede ocurrir incompatibilidad. Si predict lanza ValueError por n_features, volveremos
	# a entrenar el modelo con X y sobrescribir el modelo guardado para mantener consistencia.
	try:
		preds = model.predict(X)
	except ValueError as e:
		print("⚠️ Incompatibilidad de features entre modelo y vectorizer:", e)
		traceback.print_exc()
		# re-entrenar con X y volver a predecir
		print("🔁 Re-entrenando modelo con el vectorizer actual para mantener consistencia...")
		model.train(X)
		preds = model.predict(X)

	# Usar columna 'anomaly' para compatibilidad con la app web
	logs_df["anomaly"] = preds

	# Normalizar nombre de columna para la plantilla web (index.html espera 'log')
	if "log" not in logs_df.columns and "query" in logs_df.columns:
		logs_df["log"] = logs_df["query"].astype(str)

	print("🚨 Resultados:")
	print(logs_df)

	return logs_df


if __name__ == "__main__":
	detectar_anomalias()
