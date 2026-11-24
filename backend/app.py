from flask import Flask, jsonify
from flask_cors import CORS

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
    return jsonify({
        "status": "healthy"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)