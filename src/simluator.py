import random

class LogSimulator:
    """
    Genera logs falsos con tráfico normal + ataques.
    """

    NORMAL_QUERIES = [
        "SELECT * FROM clientes WHERE id = 1;",
        "INSERT INTO ventas VALUES (1, 100, '2024-01-01');",
        "UPDATE productos SET stock = 10 WHERE id = 3;"
    ]

    ATTACKS = [
        "SELECT * FROM users WHERE name = 'admin' OR 1=1;",
        "DROP TABLE clientes;",
        "SELECT * FROM cuentas; --",
    ]
    
    def generate_log(self):
        if random.random() < 0.2:  # 20% ataques
            query = random.choice(self.ATTACKS)
        else:
            query = random.choice(self.NORMAL_QUERIES)

        return f"timestamp={random.random()} user=juan ip=192.168.1.{random.randint(1,255)} statement: {query}"
