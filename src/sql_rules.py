import re

SQL_INJECTION_RULES = [
    {
        "name": "Tautología",
        "pattern": r"(?i)\bOR\b\s+1\s*=\s*1",
        "severity": "high"
    },
    {
        "name": "Comentario SQL",
        "pattern": r"(--|#|/\*)",
        "severity": "medium"
    },
    {
        "name": "UNION SELECT",
        "pattern": r"(?i)\bUNION\b\s+\bSELECT\b",
        "severity": "high"
    },
    {
        "name": "DROP TABLE",
        "pattern": r"(?i)\bDROP\b\s+\bTABLE\b",
        "severity": "critical"
    },
    {
        "name": "DELETE sin WHERE",
        "pattern": r"(?i)\bDELETE\b\s+\bFROM\b\s+\w+\s*;?\s*$",
        "severity": "high"
    },
    {
        "name": "SELECT *",
        "pattern": r"(?i)\bSELECT\b\s+\*",
        "severity": "low"
    }
]


def match_rules(text: str):
    """
    Devuelve lista de reglas activadas
    """
    if not text:
        return []

    matches = []
    for rule in SQL_INJECTION_RULES:
        if re.search(rule["pattern"], text):
            matches.append(rule)

    return matches
