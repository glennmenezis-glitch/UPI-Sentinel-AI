
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_connection, init_db
from datetime import datetime
from models.fraud_detector import analyze_transaction
from models.network_analyzer import analyze_network
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




@app.route("/api/network", methods=["GET"])
def get_network():
    connection = get_connection()

    try:
        result = analyze_network(connection)
        return jsonify(result)

    finally:
        connection.close()


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE risk_level = 'High'
    """)
    high_risk = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE risk_level = 'Medium'
    """)
    medium_risk = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE risk_level = 'Low'
    """)
    low_risk = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()[0]

    connection.close()

    return jsonify({
        "total_transactions": total_transactions,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "total_alerts": total_alerts
    })


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM alerts
        ORDER BY id DESC
    """)

    alerts = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jsonify(alerts)


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

    connection = None

    try:
        amount = float(data["amount"])

        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400

        connection = get_connection()

        # Analyze before inserting, so only previous transactions are counted
        result = analyze_transaction(
            amount,
            str(data["sender_id"]),
            str(data["receiver_id"]),
            connection
        )

        cursor = connection.cursor()

        status = (
            "Flagged" if result["risk_level"] == "High"
            else "Confirmation Required" if result["risk_level"] == "Medium"
            else "Allowed"
        )

        cursor.execute("""
            INSERT INTO transactions
            (transaction_id, sender_id, receiver_id, amount,
             transaction_time, risk_score, risk_level, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(data["transaction_id"]),
            str(data["sender_id"]),
            str(data["receiver_id"]),
            amount,
            datetime.now().isoformat(),
            result["risk_score"],
            result["risk_level"],
            status
        ))

        if result["risk_level"] in ["Medium", "High"]:
            cursor.execute("""
                INSERT INTO alerts (transaction_id, risk_level, message)
                VALUES (?, ?, ?)
            """, (
                str(data["transaction_id"]),
                result["risk_level"],
                ", ".join(result["reasons"])
            ))

        connection.commit()

        return jsonify({
            "message": "Transaction analyzed successfully!",
            "transaction_id": data["transaction_id"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "action": result["action"],
            "status": status,
            "reasons": result["reasons"]
        }), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid transaction amount"}), 400

    except sqlite3.IntegrityError:
        return jsonify({"error": "Transaction ID already exists"}), 409

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
