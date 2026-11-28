
from datetime import datetime, timedelta


def analyze_transaction(amount, sender_id, receiver_id, connection):

    risk_score = 0
    reasons = []

    # Rule 1: Check transaction amount
    if amount > 10000:
        risk_score += 40
        reasons.append("Unusually large transaction amount")

    # Rule 2: Check whether recipient is new
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE sender_id = ? AND receiver_id = ?
    """, (sender_id, receiver_id))

    recipient_count = cursor.fetchone()[0]

    if recipient_count == 0:
        risk_score += 30
        reasons.append("First transaction to this recipient")

    # Rule 3: Check transaction frequency
    five_minutes_ago = (
        datetime.now() - timedelta(minutes=5)
    ).isoformat()

    cursor.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE sender_id = ?
        AND transaction_time >= ?
    """, (sender_id, five_minutes_ago))

    transaction_count = cursor.fetchone()[0]

    if transaction_count >= 3:
        risk_score += 30
        reasons.append("Frequent transactions detected")

    # Determine risk level
    if risk_score >= 60:
        risk_level = "High"
        action = "FLAG_FOR_REVIEW"

    elif risk_score >= 30:
        risk_level = "Medium"
        action = "REQUEST_CONFIRMATION"

    else:
        risk_level = "Low"
        action = "ALLOW_SIMULATION"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "action": action,
        "reasons": reasons
    }
