#!/usr/bin/env python3
"""
BounceBan email verification tool.

Usage:
    python3 tools/bounceban.py --emails "email1@co.com,email2@co.com"

Reads API key from config/api-keys.json.
Returns JSON with each email categorised as deliverable, risky, undeliverable, or unknown.
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
API_BASE = "https://api.bounceban.com/v1/verify/single"


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("bounceban")
    if not key:
        print("ERROR: No bounceban key found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return key


def verify_email(api_key, email):
    params = urllib.parse.urlencode({"email": email})
    url = f"{API_BASE}?{params}"
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", api_key)
        req.add_header("User-Agent", "JasperOS/1.0")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        # If still verifying, poll for result
        if data.get("status") == "verifying" or data.get("result") == "verifying":
            tx_id = data.get("id") or data.get("transaction_id")
            if tx_id:
                time.sleep(3)
                return poll_result(api_key, tx_id, email)

        return data
    except urllib.error.HTTPError as e:
        return {"email": email, "result": "error", "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"email": email, "result": "error", "error": str(e)}


def poll_result(api_key, tx_id, email, max_attempts=10):
    url = f"{API_BASE}/status?id={tx_id}"
    for attempt in range(max_attempts):
        try:
            req = urllib.request.Request(url)
            req.add_header("Authorization", api_key)
            req.add_header("User-Agent", "JasperOS/1.0")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            if data.get("result") not in (None, "verifying"):
                return data
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return {"email": email, "result": "unknown", "error": "Verification timed out"}


def main():
    parser = argparse.ArgumentParser(description="Verify emails via BounceBan")
    parser.add_argument("--emails", required=True, help="Comma-separated list of emails")
    args = parser.parse_args()

    api_key = load_api_key()
    emails = [e.strip() for e in args.emails.split(",") if e.strip()]

    results = {"deliverable": [], "risky": [], "undeliverable": [], "unknown": [], "error": []}

    # Verify concurrently (5 workers, well within 25 req/sec rate limit)
    max_workers = min(5, len(emails))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(verify_email, api_key, email): email for email in emails}
        for future in as_completed(futures):
            email = futures[future]
            data = future.result()
            result_status = data.get("result", "unknown")

            entry = {
                "email": email,
                "result": result_status,
                "score": data.get("score"),
                "is_disposable": data.get("is_disposable"),
                "accept_all": data.get("accept_all"),
            }

            if result_status in results:
                results[result_status].append(entry)
            else:
                results["unknown"].append(entry)

    summary = {
        "total": len(emails),
        "deliverable": len(results["deliverable"]),
        "risky": len(results["risky"]),
        "undeliverable": len(results["undeliverable"]),
        "unknown": len(results["unknown"]),
        "error": len(results["error"]),
        "results": results,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
