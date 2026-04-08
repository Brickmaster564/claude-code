#!/usr/bin/env python3
"""
Search Apollo for contacts at specified law firms.
Finds senior decision-makers and enriches their emails.

Usage:
    python3 tools/apollo_law_firm_search.py .tmp/law-firms.json
"""

import json
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
API_BASE = "https://api.apollo.io/api/v1"

LEGAL_SUFFIXES = [
    ", PLC", ", P.A.", ", LLC", ", P.C.", ", LLP", ", PLLC", ", APLC",
    ", A.P.C.", ", P.L.L.C.", " LLP", " LLC", " PLLC", " Inc.", " Inc",
    " P.A.", " P.C.", " PC", " PA",
]


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    return keys.get("apollo_api_key") or keys.get("apollo")


def api_call(api_key, endpoint, payload, retries=2):
    url = f"{API_BASE}/{endpoint}"
    payload["api_key"] = api_key
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429 and attempt < retries:
                print(f"    Rate limited, waiting 5s...", file=sys.stderr)
                time.sleep(5)
                continue
            print(f"    HTTP {e.code}: {body[:200]}", file=sys.stderr)
            return None
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            print(f"    Error: {e}", file=sys.stderr)
            return None
    return None


def clean_firm_name_for_search(name):
    """Remove legal suffixes and special chars for better Apollo matching."""
    clean = name
    for suffix in LEGAL_SUFFIXES:
        clean = clean.replace(suffix, "")
    # Remove trailing commas/spaces
    clean = clean.strip().rstrip(",").strip()
    # Replace & and + with space
    clean = clean.replace("&", " ").replace("+", " ")
    # Remove extra spaces
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def firm_name_matches(searched_firm, result_org_name):
    """Fuzzy check if Apollo result matches the searched firm."""
    if not result_org_name:
        return False

    s = clean_firm_name_for_search(searched_firm).lower()
    r = clean_firm_name_for_search(result_org_name).lower()

    # Direct containment
    if s in r or r in s:
        return True

    # Check if key words overlap (at least 2 words or 1 unique word match)
    s_words = set(s.split()) - {"the", "law", "firm", "group", "office", "offices", "of", "at", "and", "for"}
    r_words = set(r.split()) - {"the", "law", "firm", "group", "office", "offices", "of", "at", "and", "for"}

    if not s_words:
        s_words = set(s.split())
    if not r_words:
        r_words = set(r.split())

    overlap = s_words & r_words
    if len(overlap) >= 2:
        return True
    if len(overlap) >= 1 and (len(s_words) <= 2 or len(r_words) <= 2):
        return True

    return False


def pick_best_contact(people, searched_firm):
    """Pick the best contact from search results, prioritizing by role."""
    # Filter to people whose company matches
    matched = []
    for p in people:
        org_name = ""
        if p.get("organization"):
            org_name = p["organization"].get("name", "")
        elif p.get("organization_name"):
            org_name = p["organization_name"]

        if firm_name_matches(searched_firm, org_name):
            matched.append(p)

    if not matched:
        # Fallback: use all results but note the mismatch
        matched = people

    # Priority ranking by title
    priority_keywords = {
        1: ["managing partner", "senior partner", "founding partner", "name partner"],
        2: ["founder", "owner", "president", "principal"],
        3: ["marketing", "business development", "growth", "partnerships", "cmo"],
        4: ["coo", "chief operating", "administrator", "executive director", "office manager"],
        5: ["partner", "managing attorney", "managing member"],
        6: ["director", "vp", "vice president"],
        7: ["attorney", "counsel", "lawyer", "associate"],
    }

    best = None
    best_priority = 99

    for person in matched:
        title = (person.get("title") or "").lower()
        priority = 8  # default

        for p, keywords in priority_keywords.items():
            if any(kw in title for kw in keywords):
                priority = p
                break

        if priority < best_priority:
            best_priority = priority
            best = person

    return best or (matched[0] if matched else None)


def search_firm(api_key, firm_name):
    """Search Apollo for people at this firm."""
    clean = clean_firm_name_for_search(firm_name)

    payload = {
        "q_keywords": clean,
        "person_seniorities": ["owner", "founder", "c_suite", "vp", "director", "manager"],
        "per_page": 10,
        "page": 1,
    }

    result = api_call(api_key, "mixed_people/search", payload)
    if not result or not result.get("people"):
        # Try broader search without seniority filter
        payload.pop("person_seniorities")
        payload["per_page"] = 5
        result = api_call(api_key, "mixed_people/search", payload)
        if not result or not result.get("people"):
            return None

    best = pick_best_contact(result["people"], firm_name)
    if not best:
        return None

    org_name = ""
    if best.get("organization"):
        org_name = best["organization"].get("name", "")

    return {
        "firm_name": firm_name,
        "apollo_org_name": org_name,
        "name": best.get("name", ""),
        "first_name": best.get("first_name", ""),
        "last_name": best.get("last_name", ""),
        "title": best.get("title", ""),
        "email": best.get("email", ""),
        "email_status": best.get("email_status", ""),
        "apollo_id": best.get("id", ""),
        "linkedin_url": best.get("linkedin_url", ""),
    }


def enrich_person(api_key, person):
    """Enrich a person to get their email via people/match."""
    payload = {
        "reveal_personal_emails": True,
    }
    if person.get("apollo_id"):
        payload["id"] = person["apollo_id"]
    if person.get("linkedin_url"):
        payload["linkedin_url"] = person["linkedin_url"]
    if person.get("first_name"):
        payload["first_name"] = person["first_name"]
    if person.get("last_name"):
        payload["last_name"] = person["last_name"]
    if person.get("firm_name"):
        payload["organization_name"] = person["firm_name"]

    result = api_call(api_key, "people/match", payload)
    if result and result.get("person"):
        p = result["person"]
        email = p.get("email") or ""
        status = p.get("email_status") or ""
        return email, status
    return "", ""


def main():
    api_key = load_api_key()
    if not api_key:
        print("ERROR: No Apollo API key found in config/api-keys.json")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 tools/apollo_law_firm_search.py <firms-json-file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        firms = json.load(f)

    print(f"Searching Apollo for {len(firms)} law firms...\n")

    results = []
    no_match = []

    # Phase 1: Search for contacts
    for i, firm in enumerate(firms):
        print(f"[{i+1}/{len(firms)}] {firm}...", flush=True)
        result = search_firm(api_key, firm)

        if result:
            email_str = result.get("email") or "needs enrichment"
            print(f"  -> {result['name']} | {result['title']} | {email_str}")
            results.append(result)
        else:
            print(f"  -> NO MATCH")
            no_match.append(firm)

        time.sleep(0.3)

    # Phase 2: Enrich contacts without emails
    need_enrichment = [r for r in results if not r.get("email")]
    if need_enrichment:
        print(f"\n--- Enriching {len(need_enrichment)} contacts for emails ---\n")
        for i, person in enumerate(need_enrichment):
            print(f"  [{i+1}/{len(need_enrichment)}] {person['name']} @ {person['firm_name']}...", flush=True)
            email, status = enrich_person(api_key, person)
            if email:
                person["email"] = email
                person["email_status"] = status
                print(f"    -> {email} ({status})")
            else:
                print(f"    -> no email found")
            time.sleep(0.3)

    # Write output
    output = {
        "found": results,
        "no_match": no_match,
        "stats": {
            "total_firms": len(firms),
            "matched": len(results),
            "no_match": len(no_match),
            "with_email": len([r for r in results if r.get("email")]),
            "without_email": len([r for r in results if not r.get("email")]),
        },
    }

    output_path = Path(__file__).parent.parent / ".tmp" / "law-firm-prospects.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary
    with_email = [r for r in results if r.get("email")]
    without_email = [r for r in results if not r.get("email")]

    print(f"\n{'='*50}")
    print(f"SEARCH COMPLETE")
    print(f"{'='*50}")
    print(f"Firms searched:  {len(firms)}")
    print(f"Contacts found:  {len(results)}")
    print(f"No match:        {len(no_match)}")
    print(f"With email:      {len(with_email)}")
    print(f"Without email:   {len(without_email)}")

    if no_match:
        print(f"\nNo match: {', '.join(no_match)}")

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
