import matplotlib.pyplot as plt

class Visualizer:
    """
    Genera gráficas simples.
    """

    def anomalies_by_hour(self, df):
        df["hour"] = df["timestamp"].dt.hour
        counts = df.groupby("hour")["anomaly"].apply(lambda x: (x == -1).sum())

        plt.figure()
        counts.plot(kind="bar")
        plt.title("Anomalías por hora")
        plt.xlabel("Hora del día")
        plt.ylabel("Número de anomalías")
        plt.show()
