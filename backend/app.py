
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_connection, init_db
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "project": "UPI Sentinel AI",
        "message": "UPI Fraud Detection Backend is running!",
        "status": "success"
    })


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})


@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")

    transactions = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jsonify(transactions)


@app.route("/api/transactions", methods=["POST"])
def add_transaction():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    required_fields = [
        "transaction_id",
        "sender_id",
        "receiver_id",
        "amount"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        amount = float(data["amount"])

        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO transactions
            (transaction_id, sender_id, receiver_id, amount, transaction_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(data["transaction_id"]),
            str(data["sender_id"]),
            str(data["receiver_id"]),
            amount,
            datetime.now().isoformat()
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "message": "Transaction added successfully!",
            "transaction_id": data["transaction_id"]
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid transaction amount"}), 400

    except sqlite3.IntegrityError:
        return jsonify({"error": "Transaction ID already exists"}), 409


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
