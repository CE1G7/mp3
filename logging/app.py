import json
import os
from datetime import datetime, timezone
from flask import Flask, request

app = Flask(__name__)

LOG_FILE = os.environ.get("LOG_FILE", "logs/all.jsonl")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

@app.route("/log", methods=["POST"])
def receive_log():
    entry = request.get_json(force=True)
    entry["received_at"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(entry, flush=True)
    return "", 204

app.run(host="0.0.0.0", port=9000)
