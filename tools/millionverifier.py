#!/usr/bin/env python3
"""
MillionVerifier email verification tool.

Usage:
    python3 tools/millionverifier.py --emails "email1@co.com,email2@co.com"

Reads API key from config/api-keys.json.
Returns JSON with each email categorised as good, risky, or bad.
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
API_BASE = "https://api.millionverifier.com/api/v3/"


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("millionverifier")
    if not key:
        print("ERROR: No millionverifier key found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return key


def verify_email(api_key, email, timeout=20):
    params = urllib.parse.urlencode({"api": api_key, "email": email, "timeout": timeout})
    url = f"{API_BASE}?{params}"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "JasperOS/1.0")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"email": email, "quality": "error", "error": str(e)}
    except Exception as e:
        return {"email": email, "quality": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Verify emails via MillionVerifier")
    parser.add_argument("--emails", required=True, help="Comma-separated list of emails")
    args = parser.parse_args()

    api_key = load_api_key()
    emails = [e.strip() for e in args.emails.split(",") if e.strip()]

    results = {"good": [], "risky": [], "bad": [], "error": []}

    for i, email in enumerate(emails):
        result = verify_email(api_key, email)
        quality = result.get("quality", "error")

        entry = {
            "email": email,
            "quality": quality,
            "result": result.get("result", ""),
            "subresult": result.get("subresult", ""),
        }

        if quality in results:
            results[quality].append(entry)
        else:
            results["error"].append(entry)

        # Respect rate limit (160 req/sec) — small delay for safety
        if i < len(emails) - 1:
            time.sleep(0.01)

    summary = {
        "total": len(emails),
        "good": len(results["good"]),
        "risky": len(results["risky"]),
        "bad": len(results["bad"]),
        "error": len(results["error"]),
        "results": results,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
