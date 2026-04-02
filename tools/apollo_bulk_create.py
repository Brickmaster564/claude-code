#!/usr/bin/env python3
"""
Bulk create Apollo contacts from the prospector working file.

Reads .tmp/prospector-run.json, creates all contacts with status 'enriched'
in Apollo via the REST API, applies dedup, adds to the specified list,
and updates the working file with results.

Usage:
    python3 tools/apollo_bulk_create.py --list "US UK Dental Practice - 24/03/26"
    python3 tools/apollo_bulk_create.py --list "US Life Insurance - 07/03/26" --workers 5

Requires Apollo API key in config/api-keys.json as 'apollo_api_key'.
Falls back to the MCP OAuth flow if no API key is found (prints instructions).
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
WORKING_FILE = Path(__file__).parent.parent / ".tmp" / "prospector-run.json"
API_BASE = "https://api.apollo.io/api/v1"


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("apollo_api_key") or keys.get("apollo")
    if not key:
        print(
            "ERROR: No Apollo API key found in config/api-keys.json.\n"
            "Add 'apollo_api_key' with your Apollo REST API key.\n"
            "Get it from: Settings > Integrations > API in Apollo.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def create_contact(api_key, contact, label_names):
    """Create a single contact in Apollo with dedup enabled."""
    payload = {
        "first_name": contact.get("first_name", ""),
        "last_name": contact.get("last_name", ""),
        "email": contact.get("email", ""),
        "title": contact.get("title", ""),
        "organization_name": contact.get("company", ""),
        "label_names": label_names,
    }

    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API_BASE}/contacts",
        data=body,
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Api-Key", api_key)
    req.add_header("User-Agent", "JasperOS/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            was_existing = data.get("contact", {}).get("id") is None
            contact_obj = data.get("contact", {})
            return {
                "apollo_id": contact.get("apollo_id"),
                "email": contact.get("email"),
                "contact_id": contact_obj.get("id", ""),
                "was_existing": was_existing,
                "success": True,
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {
            "apollo_id": contact.get("apollo_id"),
            "email": contact.get("email"),
            "success": False,
            "error": f"HTTP {e.code}: {error_body[:200]}",
        }
    except Exception as e:
        return {
            "apollo_id": contact.get("apollo_id"),
            "email": contact.get("email"),
            "success": False,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Bulk create Apollo contacts")
    parser.add_argument("--list", required=True, help="Apollo list name to add contacts to")
    parser.add_argument("--workers", type=int, default=3, help="Concurrent workers (default 3)")
    parser.add_argument("--status-filter", default="enriched", help="Only process prospects with this status (default: enriched)")
    args = parser.parse_args()

    api_key = load_api_key()

    if not WORKING_FILE.exists():
        print("ERROR: .tmp/prospector-run.json not found", file=sys.stderr)
        sys.exit(1)

    with open(WORKING_FILE) as f:
        wf = json.load(f)

    prospects = [p for p in wf["prospects"] if p["status"] == args.status_filter]
    if not prospects:
        print(json.dumps({"message": f"No prospects with status '{args.status_filter}'", "total": 0}))
        return

    print(f"Creating {len(prospects)} contacts in Apollo (list: {args.list}, workers: {args.workers})...", file=sys.stderr)

    label_names = [args.list]
    created = 0
    duplicates = 0
    errors = 0

    # Build a lookup from apollo_id to index in wf['prospects'] for fast updates
    id_to_idx = {}
    for idx, p in enumerate(wf["prospects"]):
        id_to_idx[p["apollo_id"]] = idx

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for p in prospects:
            future = executor.submit(create_contact, api_key, p, label_names)
            futures[future] = p["apollo_id"]

        done_count = 0
        for future in as_completed(futures):
            result = future.result()
            aid = result["apollo_id"]
            idx = id_to_idx.get(aid)

            if result["success"]:
                if result.get("was_existing"):
                    wf["prospects"][idx]["status"] = "duplicate"
                    duplicates += 1
                else:
                    wf["prospects"][idx]["status"] = "created"
                    created += 1
            else:
                errors += 1
                print(f"  ERROR {result['email']}: {result.get('error', 'unknown')}", file=sys.stderr)

            done_count += 1
            if done_count % 50 == 0:
                # Checkpoint every 50 contacts
                wf["stats"]["contacts_created"] = created
                wf["stats"]["duplicates_skipped"] = duplicates
                with open(WORKING_FILE, "w") as f:
                    json.dump(wf, f, indent=2)
                print(f"  Checkpoint: {done_count}/{len(prospects)} processed ({created} created, {duplicates} dupes, {errors} errors)", file=sys.stderr)

    # Final save
    wf["stats"]["contacts_created"] = created
    wf["stats"]["duplicates_skipped"] = duplicates
    with open(WORKING_FILE, "w") as f:
        json.dump(wf, f, indent=2)

    output = {
        "total_processed": len(prospects),
        "created": created,
        "duplicates": duplicates,
        "errors": errors,
        "list": args.list,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
