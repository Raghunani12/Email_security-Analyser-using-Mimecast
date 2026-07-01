import os
from flask import Flask, request, jsonify
import requests
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Production configuration
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("FLASK_ENV") == "development"

# ===========================
# CORS MIDDLEWARE
# ===========================

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response, 200

# ===========================
# TOKEN CACHE
# ===========================

token_cache = {
    "token": None,
    "expiry": 0
}

# ===========================
# GET TOKEN
# ===========================

@app.route("/api/token", methods=["POST", "OPTIONS"])
def get_token():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.json

        client_id = data.get("clientId")
        client_secret = data.get("clientSecret")
        base_url = data.get("baseUrl")

        if not client_id or not client_secret:
            return jsonify({"error": "Missing credentials"}), 400

        if (
            token_cache["token"]
            and time.time() < token_cache["expiry"]
        ):
            return jsonify({"access_token": token_cache["token"]})

        response = requests.post(
            f"{base_url}/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }
        )

        result = response.json()

        if response.status_code != 200:
            return jsonify(result), response.status_code

        token_cache["token"] = result["access_token"]
        token_cache["expiry"] = (
            time.time() + result.get("expires_in", 1800)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===========================
# SEARCH + MESSAGE INFO
# ===========================

@app.route("/api/search", methods=["POST", "OPTIONS"])
def search():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.json
        token = data["token"]
        base_url = data["baseUrl"]

        search_body = {
            "meta": {
                "pagination": {
                    "pageSize": 10
                }
            },
            "data": [
                {
                    "advancedTrackAndTraceOptions": {
                        "from": data["value"],
                        "start": data["start"],
                        "end": data["end"]
                    },
                    "searchReason": "Security investigation of vendor email traffic"
                }
            ]
        }

        search_response = requests.post(
            f"{base_url}/api/message-finder/search",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=search_body
        )

        search_data = search_response.json()

        tracked_emails = (
            search_data
            .get("data", [{}])[0]
            .get("trackedEmails", [])
        )

        if not tracked_emails:
            return jsonify({"error": "No messages found"}), 404

        top_email = tracked_emails[0]
        message_id = top_email.get("id")

        if not message_id:
            return jsonify({"error": "Message ID missing"}), 400

        info_response = requests.post(
            f"{base_url}/api/message-finder/get-message-info",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "data": [{"id": message_id}]
            }
        )

        message_info = info_response.json()

        return jsonify({
            "tracking": top_email,
            "messageInfo": message_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===========================
# HEALTH CHECK
# ===========================

@app.route("/")
def home():
    return jsonify({"status": "Mimecast API Running", "version": "1.0"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
