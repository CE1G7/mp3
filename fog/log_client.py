import json
import os
import queue
import threading
import urllib.request

COLLECTOR = os.environ.get("COLLECTOR_URL", "http://10.30.0.10:9000/log")
NODE_NAME = os.environ.get("NODE_NAME", "unknown")
_q = queue.Queue(maxsize=1000)


def _worker():
    while True:
        entry = _q.get()
        try:
            req = urllib.request.Request(
                COLLECTOR,
                data=json.dumps(entry).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=0.5)
        except Exception:
            pass
        finally:
            _q.task_done()


threading.Thread(target=_worker, daemon=True).start()


def send_log(entry):
    entry.setdefault("node", NODE_NAME)
    try:
        _q.put_nowait(entry)
    except queue.Full:
        pass
