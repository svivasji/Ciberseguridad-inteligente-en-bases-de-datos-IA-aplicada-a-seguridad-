import re
from datetime import datetime

class FeatureExtractor:
    """
    Extrae atributos útiles para IA:
    longitud, palabras clave sospechosas, IP, usuario, etc.
    """
    
    SUSPICIOUS_KEYWORDS = ["UNION", "DROP", "INSERT", " OR 1=1", "--", "' OR '"]

    def extract_features(self, line: str):
        try:
            timestamp = self._extract_timestamp(line)
            user = self._extract_user(line)
            ip = self._extract_ip(line)
            query = self._extract_query(line)

            return {
                "timestamp": timestamp,
                "user": user,
                "ip": ip,
                "query": query,
                "query_length": len(query),
                "suspicious_count": self._count_suspicious(query)
            }
        except:
            return None

    def _extract_timestamp(self, log):
        # Ejemplo básico, adaptar al formato de PostgreSQL real
        return datetime.now()

    def _extract_user(self, log):
        match = re.search(r"user=(\w+)", log)
        return match.group(1) if match else "unknown"

    def _extract_ip(self, log):
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", log)
        return match.group(1) if match else "0.0.0.0"

    def _extract_query(self, log):
        match = re.search(r"statement:\s(.+)", log)
        return match.group(1) if match else ""

    def _count_suspicious(self, query):
        return sum(1 for key in self.SUSPICIOUS_KEYWORDS if key in query.upper())
