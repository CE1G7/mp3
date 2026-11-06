import argparse
import json
import os
import random
import time
import urllib.request
from datetime import datetime, timezone

URL = os.environ.get("COLLECTOR_URL", "http://10.30.0.10:9000/log")
THRESHOLD = 200000

CAMERAS = [
    ("cam_a", "10.10.1.128", "fog_a"),
    ("cam_b", "10.10.1.129", "fog_a"),
    ("cam_c", "10.10.2.128", "fog_b"),
]


def post(entry):
    req = urllib.request.Request(
        URL,
        data=json.dumps(entry).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=1)
    except Exception as exc:
        print("send failed:", exc, flush=True)


def event(node, client_id, client_ip, size_bytes, cpu_load):
    if size_bytes <= THRESHOLD:
        decision, offload = "local", 0
    elif cpu_load < 0.7:
        decision, offload = "split", size_bytes // 2
    else:
        decision, offload = "full_offload", size_bytes
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node": node,
        "client_ip": client_ip,
        "client_id": client_id,
        "size_bytes": size_bytes,
        "decision": decision,
        "offload_bytes": offload,
        "cpu_load": round(cpu_load, 2),
        "processing_time_ms": round(random.uniform(8, 60), 1),
        "http_status": 200,
    }


def normal(duration):
    print("baseline traffic for %ds" % duration, flush=True)
    end = time.time() + duration
    while time.time() < end:
        cid, cip, node = random.choice(CAMERAS)
        size = random.choice([80000, 150000, 260000, 410000])
        post(event(node, cid, cip, size, random.uniform(0.2, 0.6)))
        time.sleep(0.5)


def dos(duration, rate):
    print("dos: cam_a at %d req/s for %ds" % (rate, duration), flush=True)
    end = time.time() + duration
    while time.time() < end:
        for _ in range(rate):
            post(event("fog_a", "cam_a", "10.10.1.128", 120000,
                       random.uniform(0.8, 0.98)))
        time.sleep(1)


def spoof(count):
    print("spoof: cam_a identity from 10.10.1.200", flush=True)
    for _ in range(count):
        post(event("fog_a", "cam_a", "10.10.1.200", 95000, 0.5))
        time.sleep(0.2)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="all",
                   choices=["normal", "dos", "spoof", "all"])
    p.add_argument("--duration", type=int, default=15)
    p.add_argument("--rate", type=int, default=25)
    a = p.parse_args()

    if a.mode in ("normal", "all"):
        normal(a.duration)
    if a.mode in ("dos", "all"):
        dos(a.duration, a.rate)
    if a.mode in ("spoof", "all"):
        spoof(5)
    print("done", flush=True)
