#!/usr/bin/env python3
"""
DataForSEO tool — keyword research for Google Ads campaigns.

Uses Live endpoints (real-time, ~10x cost of Standard but no polling).
Auth: HTTP Basic. Login + password from config/api-keys.json.

Commands:
    search-volume     Get Google Ads search volume + CPC + competition for a list of keywords.
    keyword-ideas     Get keyword ideas from a seed (DataForSEO Labs, Google, US).
    keyword-suggestions  Long-tail variants of a seed keyword.
    search-intent     Classify keywords as informational/navigational/commercial/transactional.
    keywords-for-site  Pull keywords a competitor domain ranks/bids for.

Defaults: location_code=2840 (US), language_code=en.
"""

import argparse
import base64
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG = Path(__file__).parent.parent / "config" / "api-keys.json"
BASE = "https://api.dataforseo.com/v3"


def auth_header():
    keys = json.loads(CONFIG.read_text())
    login = keys["dataforseo_login"]
    pwd = keys["dataforseo_password"]
    raw = f"{login}:{pwd}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def call(path, payload):
    """POST a list-wrapped payload (DataForSEO convention) and return the JSON response."""
    url = BASE + path
    body = json.dumps([payload]).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", auth_header())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}:", e.read().decode()[:500], file=sys.stderr)
        sys.exit(1)


def cmd_search_volume(args):
    keywords = read_keywords(args.keywords, args.input)
    payload = {
        "keywords": keywords,
        "location_code": args.location,
        "language_code": args.language,
    }
    if args.search_partners:
        payload["search_partners"] = True
    res = call("/keywords_data/google_ads/search_volume/live", payload)
    write_out(args.output, res)


def cmd_keyword_ideas(args):
    payload = {
        "keywords": [args.seed] if args.seed else read_keywords(args.keywords, args.input),
        "location_code": args.location,
        "language_code": args.language,
        "limit": args.limit,
        "include_seed_keyword": True,
        "order_by": ["keyword_info.search_volume,desc"],
    }
    if args.filter_min_volume:
        payload["filters"] = [["keyword_info.search_volume", ">=", args.filter_min_volume]]
    res = call("/dataforseo_labs/google/keyword_ideas/live", payload)
    write_out(args.output, res)


def cmd_keyword_suggestions(args):
    payload = {
        "keyword": args.seed,
        "location_code": args.location,
        "language_code": args.language,
        "limit": args.limit,
        "include_seed_keyword": True,
        "order_by": ["keyword_info.search_volume,desc"],
    }
    res = call("/dataforseo_labs/google/keyword_suggestions/live", payload)
    write_out(args.output, res)


def cmd_search_intent(args):
    keywords = read_keywords(args.keywords, args.input)
    payload = {
        "keywords": keywords[:1000],
        "language_code": args.language,
    }
    res = call("/dataforseo_labs/google/search_intent/live", payload)
    write_out(args.output, res)


def cmd_keywords_for_site(args):
    payload = {
        "target": args.target,
        "location_code": args.location,
        "language_code": args.language,
        "limit": args.limit,
        "order_by": ["keyword_info.search_volume,desc"],
    }
    if args.filter_min_volume:
        payload["filters"] = [["keyword_info.search_volume", ">=", args.filter_min_volume]]
    res = call("/dataforseo_labs/google/keywords_for_site/live", payload)
    write_out(args.output, res)


def read_keywords(inline, input_path):
    if inline:
        return [k.strip() for k in inline if k.strip()]
    if input_path:
        text = Path(input_path).read_text()
        try:
            j = json.loads(text)
            if isinstance(j, list):
                return [str(x).strip() for x in j if str(x).strip()]
        except json.JSONDecodeError:
            pass
        return [ln.strip() for ln in text.splitlines() if ln.strip()]
    print("ERROR: provide --keywords or --input", file=sys.stderr)
    sys.exit(1)


def write_out(path, data):
    if path:
        Path(path).write_text(json.dumps(data, indent=2))
        print(f"Wrote {path}")
    else:
        print(json.dumps(data, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    def add_common(s):
        s.add_argument("--location", type=int, default=2840, help="DataForSEO location code (default 2840 = US)")
        s.add_argument("--language", default="en")
        s.add_argument("-o", "--output", help="Write JSON to this file")

    s1 = sp.add_parser("search-volume", help="Google Ads search volume + CPC + competition")
    s1.add_argument("--keywords", nargs="*")
    s1.add_argument("--input")
    s1.add_argument("--search-partners", action="store_true")
    add_common(s1)
    s1.set_defaults(func=cmd_search_volume)

    s2 = sp.add_parser("keyword-ideas", help="Keyword ideas (DataForSEO Labs)")
    s2.add_argument("--seed")
    s2.add_argument("--keywords", nargs="*")
    s2.add_argument("--input")
    s2.add_argument("--limit", type=int, default=700)
    s2.add_argument("--filter-min-volume", type=int)
    add_common(s2)
    s2.set_defaults(func=cmd_keyword_ideas)

    s3 = sp.add_parser("keyword-suggestions", help="Long-tail suggestions for a seed")
    s3.add_argument("--seed", required=True)
    s3.add_argument("--limit", type=int, default=700)
    add_common(s3)
    s3.set_defaults(func=cmd_keyword_suggestions)

    s4 = sp.add_parser("search-intent", help="Classify search intent")
    s4.add_argument("--keywords", nargs="*")
    s4.add_argument("--input")
    add_common(s4)
    s4.set_defaults(func=cmd_search_intent)

    s5 = sp.add_parser("keywords-for-site", help="Pull keywords a competitor domain targets")
    s5.add_argument("--target", required=True, help="Domain, e.g. ethoslife.com")
    s5.add_argument("--limit", type=int, default=700)
    s5.add_argument("--filter-min-volume", type=int)
    add_common(s5)
    s5.set_defaults(func=cmd_keywords_for_site)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
