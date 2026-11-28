
import sqlite3
from models.fraud_detector import analyze_transaction

# Create a temporary database for testing
connection = sqlite3.connect(":memory:")

connection.execute("""
    CREATE TABLE transactions (
        sender_id TEXT,
        receiver_id TEXT,
        transaction_time TEXT
    )
""")

# Test a large transaction to a new recipient
result = analyze_transaction(
    amount=15000,
    sender_id="USER001",
    receiver_id="USER002",
    connection=connection
)

print("Fraud Detection Test Result:")
print(result)

connection.close()
