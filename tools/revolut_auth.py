#!/usr/bin/env python3
"""One-shot Revolut auth helper. Run this, visit the URL, paste the code."""

import jwt
import time
import uuid
import json
import requests
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PRIVATE_KEY_PATH = BASE_DIR / "config" / "revolut_private.pem"
TOKEN_PATH = BASE_DIR / "config" / "revolut-token.json"

CLIENT_ID = "mOgeIWc1kuh21EgE-wNNNJAQ4NTGE5Lqy4B6jUKRTLk"
REDIRECT_URI = "https://nalupartners.com/revolut/callback"
ISS = "nalupartners.com"

AUTH_URL = (
    f"https://business.revolut.com/app-confirm"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
)

print("\n=== Revolut Auth ===\n")
print("1. Open this URL in your browser (must be logged into Revolut Business):\n")
print(f"   {AUTH_URL}\n")
print("2. Approve access.")
print("3. You'll be redirected to a URL like:")
print(f"   {REDIRECT_URI}?code=XXXX\n")
print("4. Copy just the code value and paste it below.\n")

code = input("Paste code here: ").strip()

# Strip full URL if pasted by mistake
if "code=" in code:
    code = code.split("code=")[-1].split("&")[0].strip()

print(f"\nExchanging code: {code[:20]}...")

private_key = PRIVATE_KEY_PATH.read_text()
now = int(time.time())
payload = {
    "iss": ISS,
    "sub": CLIENT_ID,
    "aud": "https://revolut.com",
    "iat": now,
    "nbf": now,
    "exp": now + 120,
    "jti": str(uuid.uuid4()),
}
assertion = jwt.encode(payload, private_key, algorithm="RS256")

resp = requests.post(
    "https://b2b.revolut.com/api/1.0/auth/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "authorization_code",
        "code": code,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": assertion,
        "client_id": CLIENT_ID,
    },
)

if resp.ok:
    data = resp.json()
    data["expires_at"] = int(time.time()) + data.get("expires_in", 2400)
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSuccess! Tokens saved to {TOKEN_PATH}")
    print(f"Access token expires in: {data.get('expires_in', '?')}s")
    print(f"Refresh token: {'present' if data.get('refresh_token') else 'MISSING'}")
else:
    print(f"\nFailed: {resp.status_code} {resp.text}")
    print("\nDebug info:")
    print(f"  JWT iss: {ISS}")
    print(f"  Client ID: {CLIENT_ID}")
    print(f"  Redirect URI: {REDIRECT_URI}")
