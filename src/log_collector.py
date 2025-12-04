import os
import glob

class LogCollector:
    """
    Se encarga de recoger logs reales o simulados.
    """
    def __init__(self, log_path="data/raw_logs/"):
        self.log_path = log_path

    def load_logs(self):
        logs = []
        for file in glob.glob(os.path.join(self.log_path, "*.log")):
            with open(file, "r", encoding="utf-8") as f:
                logs.extend(f.readlines())
        return logs
