import json
import os
from collections import defaultdict, deque
from datetime import datetime, timezone
from flask import Flask, request

app = Flask(__name__)

LOG_FILE = os.environ.get("LOG_FILE", "logs/all.jsonl")
ALERT_FILE = os.environ.get("ALERT_FILE", "logs/alerts.jsonl")
WINDOW_S = float(os.environ.get("WINDOW_S", "10"))
MAX_REQ = int(os.environ.get("MAX_REQ", "20"))
COOLDOWN_S = float(os.environ.get("COOLDOWN_S", "10"))

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

hits_by_id = defaultdict(deque)
hits_by_ip = defaultdict(deque)
ips_by_id = defaultdict(set)
last_alert = {}


def write(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")


def raise_alert(rule, detail, entry, now):
    key = (rule, entry.get("client_id"), entry.get("client_ip"))
    if now - last_alert.get(key, -COOLDOWN_S) < COOLDOWN_S:
        return
    last_alert[key] = now
    alert = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": "alert",
        "rule": rule,
        "detail": detail,
        "node": entry.get("node"),
        "client_id": entry.get("client_id"),
        "client_ip": entry.get("client_ip"),
    }
    write(ALERT_FILE, alert)
    print("ALERT:", rule, "-", detail, flush=True)


def prune(dq, now):
    while dq and now - dq[0] > WINDOW_S:
        dq.popleft()


def check_alerts(entry, now):
    cid = entry.get("client_id")
    cip = entry.get("client_ip")

    if cid:
        dq = hits_by_id[cid]
        dq.append(now)
        prune(dq, now)
        if len(dq) > MAX_REQ:
            raise_alert("rate_per_client_id",
                        "%d requests in %.0fs" % (len(dq), WINDOW_S),
                        entry, now)

    if cip:
        dq = hits_by_ip[cip]
        dq.append(now)
        prune(dq, now)
        if len(dq) > MAX_REQ:
            raise_alert("rate_per_client_ip",
                        "%d requests in %.0fs" % (len(dq), WINDOW_S),
                        entry, now)

    if cid and cip:
        seen = ips_by_id[cid]
        seen.add(cip)
        if len(seen) > 1:
            raise_alert("id_ip_mismatch",
                        "client_id seen from %s" % sorted(seen),
                        entry, now)


@app.route("/log", methods=["POST"])
def receive_log():
    entry = request.get_json(force=True)
    now = datetime.now(timezone.utc)
    entry["received_at"] = now.isoformat()
    write(LOG_FILE, entry)
    print(entry, flush=True)
    check_alerts(entry, now.timestamp())
    return "", 204


app.run(host="0.0.0.0", port=9000)
