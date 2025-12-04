import pandas as pd
from anomaly_model import AnomalyModel

class Detector:
    """
    Usa el modelo ya entrenado para marcar eventos como normales/anómalos.
    """

    def __init__(self):
        self.model = AnomalyModel()
        self.model.load()

    def detect(self, df: pd.DataFrame):
        df["anomaly"] = self.model.predict(df)
        return df
