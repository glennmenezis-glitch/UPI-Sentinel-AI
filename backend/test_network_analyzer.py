
import sqlite3
from models.network_analyzer import analyze_network

# Create a temporary database
connection = sqlite3.connect(":memory:")
connection.row_factory = sqlite3.Row

connection.execute("""
    CREATE TABLE transactions (
        sender_id TEXT,
        receiver_id TEXT,
        amount REAL
    )
""")

# Insert sample transactions
transactions = [
    ("USER001", "USER100", 5000),
    ("USER002", "USER100", 3000),
    ("USER003", "USER100", 4000),
    ("USER100", "USER200", 2000),
    ("USER200", "USER300", 1500),
    ("USER300", "USER100", 1000)
]

connection.executemany("""
    INSERT INTO transactions
    (sender_id, receiver_id, amount)
    VALUES (?, ?, ?)
""", transactions)

# Run network analysis
result = analyze_network(connection)

print("Network Analysis Results:")
print(result)

connection.close()
