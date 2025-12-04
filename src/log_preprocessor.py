from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from config import VECTORIZER_PATH
from pathlib import Path


class LogPreprocessor:
    def __init__(self):
        # Crear el vectorizador por defecto; puede ser reemplazado cargando uno guardado
        self.vectorizer = TfidfVectorizer()

    def fit_transform(self, logs):
        X = self.vectorizer.fit_transform(logs)
        return X

    def transform(self, logs):
        return self.vectorizer.transform(logs)

    def save(self, path: str = None):
        p = Path(path or VECTORIZER_PATH)
        if p.parent and not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, str(p))

    def load(self, path: str = None):
        p = Path(path or VECTORIZER_PATH)
        if p.exists():
            self.vectorizer = joblib.load(str(p))
            return True
        return False
