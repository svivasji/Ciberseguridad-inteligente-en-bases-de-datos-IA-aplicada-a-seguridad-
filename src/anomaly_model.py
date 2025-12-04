import joblib
import os
from pathlib import Path
from sklearn.ensemble import IsolationForest
from config import MODEL_PATH

class AnomalyModel:

    def __init__(self):
        self.model = None

    def train(self, X):
        self.model = IsolationForest(contamination=0.05)
        self.model.fit(X)
        # Asegurar que la carpeta destino exista antes de guardar
        model_path = Path(MODEL_PATH)
        if model_path.parent and not model_path.parent.exists():
            os.makedirs(model_path.parent, exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        print(f"✔ Modelo entrenado guardado en {MODEL_PATH}")

    def load(self):
        # joblib.load lanzará si no existe; el llamador debe manejarlo
        self.model = joblib.load(MODEL_PATH)

    def predict(self, X):
        if self.model is None:
            try:
                self.load()
            except Exception:
                # Si no existe un modelo guardado, entrenar con los datos actuales
                self.train(X)
        return self.model.predict(X)
