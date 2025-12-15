from sql_rules import match_rules

def detect_by_rules(log_text: str):
    """
    Devuelve:
    - is_anomalous (bool)
    - reasons (lista de reglas)
    """
    rules = match_rules(log_text)

    if not rules:
        return False, []

    # Si alguna regla es crítica o alta se considera anomalía
    severities = {r["severity"] for r in rules}
    is_anomalous = bool(severities & {"high", "critical"})

    return is_anomalous, rules
