#!/usr/bin/env python3
"""Run API tests and write results to api_run.txt in project root."""
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://api.meetapexneural.com"
OUT = Path(__file__).resolve().parent.parent / "api_run.txt"
lines = []


def req(method, path, data=None):
    url = f"{BASE}{path}"
    r = urllib.request.Request(url, data=data, method=method)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=15) as res:
            body = res.read().decode()
            return res.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)


def run():
    lines.append("=== 1. GET /health ===")
    code, body = req("GET", "/health")
    lines.append(body)
    lines.append(f"HTTP {code}\n")

    lines.append("=== 2. POST /leads (lead_id) ===")
    code, body = req("POST", "/leads", data=b'{"lead_id":"run-py-001","campaign_name":"DubaiCamp"}')
    lines.append(body[:500] if len(body) > 500 else body)
    lines.append(f"\nHTTP {code}\n")

    lines.append("=== 3. POST /leads (email) ===")
    code, body = req("POST", "/leads", data=b'{"email":"run-py@example.com","campaign_name":"Webinar2025"}')
    lines.append(body[:500] if len(body) > 500 else body)
    lines.append(f"\nHTTP {code}\n")

    lines.append("=== 4. GET /leads ===")
    code, body = req("GET", "/leads")
    lines.append(body[:1000] if len(body) > 1000 else body)
    lines.append(f"\nHTTP {code}\n")

    lines.append("=== 5. POST /events ===")
    code, body = req("POST", "/events", data=b'{"tracking_id":"run-py-001","event_type":"open"}')
    lines.append(body)
    lines.append(f" HTTP {code}\n")

    lines.append("=== 6. GET /go (redirect) ===")
    r = urllib.request.Request(f"{BASE}/go/DubaiCamp/run-py-001", method="GET")
    r.get_method = lambda: "GET"
    try:
        with urllib.request.urlopen(r, timeout=10) as res:
            lines.append(f"HTTP {res.status}")
    except urllib.error.HTTPError as e:
        if e.code == 302:
            lines.append(f"HTTP 302 (redirect) Location: {e.headers.get('Location', '')}")
        else:
            lines.append(f"HTTP {e.code}")
    except Exception as e:
        lines.append(str(e))

    content = "\n".join(lines)
    OUT.write_text(content)
    print(content)
    print(f"\nResults also written to {OUT}")


if __name__ == "__main__":
    run()
