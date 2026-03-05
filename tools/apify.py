#!/usr/bin/env python3
"""
Apify LinkedIn profile scraper tool.

Usage:
    python3 tools/apify.py scrape-profiles --urls "https://linkedin.com/in/person1,https://linkedin.com/in/person2"

Runs the dev_fusion/Linkedin-Profile-Scraper actor on Apify and returns
profile data including recent LinkedIn posts (updates).

Reads API key from config/api-keys.json.
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
ACTOR_ID = "dev_fusion/Linkedin-Profile-Scraper"
API_BASE = "https://api.apify.com/v2"
POLL_INTERVAL = 10  # seconds between status checks
MAX_WAIT = 600  # max seconds to wait for actor run


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("apify")
    if not key:
        print("ERROR: No apify key found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(token, method, endpoint, data=None):
    separator = "&" if "?" in endpoint else "?"
    url = f"{API_BASE}{endpoint}{separator}token={token}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "JasperOS/1.0")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}
    except Exception as e:
        return {"error": str(e)}


def run_actor(token, linkedin_urls):
    """Start the LinkedIn Profile Scraper actor and wait for results."""
    # Start the actor run
    actor_input = {
        "profileUrls": linkedin_urls
    }

    print(f"Starting Apify actor for {len(linkedin_urls)} profiles...", file=sys.stderr)
    run_result = api_request(token, "POST", f"/acts/{ACTOR_ID}/runs", data=actor_input)

    if "error" in run_result:
        return {"error": run_result["error"], "detail": run_result.get("detail", "")}

    run_id = run_result["data"]["id"]
    dataset_id = run_result["data"]["defaultDatasetId"]
    print(f"Actor run started: {run_id}", file=sys.stderr)

    # Poll for completion
    elapsed = 0
    while elapsed < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        status_result = api_request(token, "GET", f"/actor-runs/{run_id}")
        if "error" in status_result:
            print(f"Warning: status check failed: {status_result['error']}", file=sys.stderr)
            continue

        status = status_result["data"]["status"]
        print(f"  Status: {status} ({elapsed}s elapsed)", file=sys.stderr)

        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            return {"error": f"Actor run {status}", "run_id": run_id}

    if elapsed >= MAX_WAIT:
        return {"error": f"Actor run timed out after {MAX_WAIT}s", "run_id": run_id}

    # Fetch dataset results
    dataset_result = api_request(token, "GET", f"/datasets/{dataset_id}/items")
    if isinstance(dataset_result, list):
        return parse_profiles(dataset_result)
    elif "error" in dataset_result:
        return {"error": dataset_result["error"]}
    else:
        return parse_profiles(dataset_result.get("items", dataset_result))


def parse_profiles(items):
    """Extract relevant fields from scraped LinkedIn profiles."""
    profiles = []
    for item in items:
        profile = {
            "linkedin_url": item.get("linkedinUrl", ""),
            "full_name": item.get("fullName", ""),
            "first_name": item.get("firstName", ""),
            "last_name": item.get("lastName", ""),
            "headline": item.get("headline", ""),
            "company": item.get("companyName", ""),
            "is_creator": item.get("isCreator", False),
            "followers": item.get("followers", 0),
            "has_recent_posts": False,
            "recent_post_text": ""
        }

        # Check for recent posts (updates)
        updates_0_text = item.get("updates/0/postText") or item.get("updates", [{}])[0].get("postText", "") if isinstance(item.get("updates"), list) else ""
        # Try flat CSV-style keys first (from Apify dataset)
        if not updates_0_text:
            for key in item:
                if key.startswith("updates") and "postText" in key:
                    updates_0_text = item[key]
                    break

        if updates_0_text:
            profile["has_recent_posts"] = True
            profile["recent_post_text"] = updates_0_text[:200]

        profiles.append(profile)

    active = [p for p in profiles if p["has_recent_posts"]]
    inactive = [p for p in profiles if not p["has_recent_posts"]]

    return {
        "total": len(profiles),
        "active_posters": len(active),
        "inactive": len(inactive),
        "profiles": profiles
    }


def scrape_profiles(token, urls):
    """Main entry point for scraping LinkedIn profiles."""
    if not urls:
        return {"error": "No URLs provided"}

    return run_actor(token, urls)


def main():
    parser = argparse.ArgumentParser(description="Apify LinkedIn profile scraper")
    subparsers = parser.add_subparsers(dest="command")

    scrape_cmd = subparsers.add_parser("scrape-profiles", help="Scrape LinkedIn profiles")
    scrape_cmd.add_argument("--urls", required=True, help="Comma-separated LinkedIn profile URLs")

    args = parser.parse_args()
    token = load_api_key()

    if args.command == "scrape-profiles":
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]
        result = scrape_profiles(token, urls)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
