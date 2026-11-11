import json, glob, os, statistics, sys

LEGIT = {"cam_a", "cam_b", "cam_c"}
PHASES = ["baseline", "attack", "mitigated", "botnet", "rotate", "spoof"]
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")


def load(path):
    rows = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and line != "[]":
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except FileNotFoundError:
        pass
    return rows


def pctl(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round((p / 100) * (len(s) - 1)))))
    return s[k]


def summarize(rows):
    legit = [r for r in rows if r.get("client_id") in LEGIT]
    ok = [r for r in legit if r.get("http_status") == 200]
    lat = [r["processing_time_ms"] for r in ok if "processing_time_ms" in r]
    rej_legit = sum(1 for r in legit if r.get("http_status") == 429)
    rej_atk = sum(1 for r in rows if r.get("client_id") not in LEGIT and r.get("http_status") == 429)
    atk_req = sum(1 for r in rows if r.get("client_id") not in LEGIT)
    zb = [r for r in rows if r.get("node") == "fog_b" and r.get("client_id") in LEGIT and r.get("http_status") == 200]
    zb_lat = [r["processing_time_ms"] for r in zb if "processing_time_ms" in r]
    return {
        "legit_ok": len(ok),
        "mean_ms": round(statistics.mean(lat), 1) if lat else 0.0,
        "p95_ms": round(pctl(lat, 95), 1),
        "rej_legit": rej_legit,
        "rej_atk": rej_atk,
        "atk_req": atk_req,
        "zoneb_ok": len(zb),
        "zoneb_mean_ms": round(statistics.mean(zb_lat), 1) if zb_lat else 0.0,
    }


def main():
    data = {}
    for ph in PHASES:
        rows = load(os.path.join(RESULTS, f"{ph}_all.jsonl"))
        if rows:
            data[ph] = summarize(rows)

    cols = [("legit_ok", "legit ok"), ("mean_ms", "mean ms"), ("p95_ms", "p95 ms"),
            ("rej_legit", "rej legit"), ("rej_atk", "rej atk"), ("atk_req", "atk req"),
            ("zoneb_ok", "zB ok"), ("zoneb_mean_ms", "zB mean ms")]

    print("\n=== Section 5 summary (legitimate cameras cam_a/b/c) ===\n")
    hdr = "phase".ljust(11) + "".join(h.ljust(11) for _, h in cols)
    print(hdr)
    print("-" * len(hdr))
    for ph in PHASES:
        if ph in data:
            print(ph.ljust(11) + "".join(str(data[ph][k]).ljust(11) for k, _ in cols))

    print("\n=== LaTeX ===\n")
    print(r"\begin{tabular}{l" + "r" * len(cols) + "}")
    print(r"\toprule")
    print("Phase & " + " & ".join(h for _, h in cols) + r" \\")
    print(r"\midrule")
    for ph in PHASES:
        if ph in data:
            print(ph + " & " + " & ".join(str(data[ph][k]) for k, _ in cols) + r" \\")
    print(r"\bottomrule")
    print(r"\end{tabular}")

    for ph in ["spoof", "botnet", "rotate"]:
        ap = os.path.join(RESULTS, f"{ph}_alerts.jsonl")
        al = load(ap)
        if al:
            print(f"\n=== {ph} alerts ({len(al)}) ===")
            for a in al[:6]:
                print(json.dumps(a))


if __name__ == "__main__":
    main()
