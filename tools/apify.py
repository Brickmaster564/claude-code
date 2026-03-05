#!/usr/bin/env python3
"""
Apify scraper tools (LinkedIn + X/Twitter).

Usage:
    python3 tools/apify.py scrape-profiles --urls "https://linkedin.com/in/person1,https://linkedin.com/in/person2"
    python3 tools/apify.py scrape-comments --usernames "person1,person2"
    python3 tools/apify.py scrape-tweets --handles "sabrisuby,TheJeremyHaynes" [--max-per-user 5]

scrape-profiles: Runs dev_fusion/Linkedin-Profile-Scraper to get profile data
                 including recent posts (updates).
scrape-comments: Runs apimaestro/linkedin-profile-comments to get comments
                 the user has made on other people's posts.
scrape-tweets:   Runs apidojo/tweet-scraper to get recent tweets from X handles.

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
ACTOR_PROFILE = "dev_fusion~Linkedin-Profile-Scraper"
ACTOR_COMMENTS = "apimaestro~linkedin-profile-comments"
ACTOR_TWEETS = "apidojo~tweet-scraper"
API_BASE = "https://api.apify.com/v2"
POLL_INTERVAL = 10  # seconds between status checks
MAX_WAIT = 600  # max seconds to wait for actor run
COMMENTS_ACTIVE_MONTHS = 9  # comments within this many months = active


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


def run_actor(token, actor_id, actor_input, label=""):
    """Start an Apify actor and wait for results."""
    print(f"Starting Apify actor {actor_id} {label}...", file=sys.stderr)
    run_result = api_request(token, "POST", f"/acts/{actor_id}/runs", data=actor_input)

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
    return dataset_result if isinstance(dataset_result, list) else dataset_result.get("items", dataset_result)


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
        updates = item.get("updates")
        updates_0_text = ""
        if isinstance(updates, list) and len(updates) > 0:
            updates_0_text = item.get("updates/0/postText") or updates[0].get("postText", "")
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
    """Scrape LinkedIn profiles for post activity."""
    if not urls:
        return {"error": "No URLs provided"}

    raw = run_actor(token, ACTOR_PROFILE, {"profileUrls": urls},
                    label=f"for {len(urls)} profiles")
    if isinstance(raw, dict) and "error" in raw:
        return raw
    return parse_profiles(raw)


def scrape_comments(token, usernames):
    """Scrape LinkedIn commenting activity for given usernames."""
    if not usernames:
        return {"error": "No usernames provided"}

    results = {"total": 0, "active_commenters": 0, "inactive": 0, "profiles": []}

    for username in usernames:
        raw = run_actor(token, ACTOR_COMMENTS, {"username": username},
                        label=f"comments for {username}")
        if isinstance(raw, dict) and "error" in raw:
            results["profiles"].append({
                "username": username,
                "has_recent_comments": False,
                "comment_count": 0,
                "most_recent_comment": None,
                "error": raw["error"]
            })
            results["inactive"] += 1
            results["total"] += 1
            continue

        comments = raw if isinstance(raw, list) else []
        most_recent_ts = 0
        most_recent_date = ""
        most_recent_text = ""

        for c in comments:
            created = c.get("created_at", {})
            ts = created.get("timestamp", 0)
            if ts > most_recent_ts:
                most_recent_ts = ts
                most_recent_date = created.get("formatted", "")
                most_recent_text = (c.get("comment_text") or "")[:200]

        # Check if most recent comment is within the active window
        has_recent = False
        if most_recent_ts > 0:
            import datetime
            comment_date = datetime.datetime.fromtimestamp(most_recent_ts / 1000)
            cutoff = datetime.datetime.now() - datetime.timedelta(days=COMMENTS_ACTIVE_MONTHS * 30)
            has_recent = comment_date >= cutoff

        profile = {
            "username": username,
            "has_recent_comments": has_recent,
            "comment_count": len(comments),
            "most_recent_comment": most_recent_date,
            "most_recent_text": most_recent_text
        }
        results["profiles"].append(profile)
        results["total"] += 1
        if has_recent:
            results["active_commenters"] += 1
        else:
            results["inactive"] += 1

    return results


def scrape_tweets(token, handles, max_per_user=5):
    """Scrape recent tweets from X/Twitter handles."""
    if not handles:
        return {"error": "No handles provided"}

    # Run the actor once with all handles
    actor_input = {
        "twitterHandles": handles,
        "maxItems": max_per_user * len(handles),
        "sort": "Latest"
    }

    raw = run_actor(token, ACTOR_TWEETS, actor_input,
                    label=f"for {len(handles)} X handles")
    if isinstance(raw, dict) and "error" in raw:
        return raw

    items = raw if isinstance(raw, list) else []

    # Group tweets by author
    by_author = {}
    for tweet in items:
        author = tweet.get("author", {})
        handle = author.get("userName", "") or tweet.get("user", {}).get("screen_name", "")
        if not handle:
            # Try alternate field names
            handle = tweet.get("username", "") or tweet.get("screen_name", "")
        handle_lower = handle.lower()

        if handle_lower not in by_author:
            by_author[handle_lower] = {
                "handle": handle,
                "name": author.get("name", "") or tweet.get("user", {}).get("name", handle),
                "tweets": []
            }

        text = tweet.get("text", "") or tweet.get("full_text", "") or tweet.get("tweetText", "")
        created = tweet.get("createdAt", "") or tweet.get("created_at", "")
        likes = tweet.get("likeCount", 0) or tweet.get("favorite_count", 0)
        retweets = tweet.get("retweetCount", 0) or tweet.get("retweet_count", 0)
        is_retweet = tweet.get("isRetweet", False)

        if is_retweet:
            continue

        by_author[handle_lower]["tweets"].append({
            "text": text[:500],
            "created_at": created,
            "likes": likes,
            "retweets": retweets
        })

    # Limit tweets per user and sort by engagement
    for handle_lower in by_author:
        tweets = by_author[handle_lower]["tweets"]
        tweets.sort(key=lambda t: t.get("likes", 0) + t.get("retweets", 0), reverse=True)
        by_author[handle_lower]["tweets"] = tweets[:max_per_user]

    return {
        "total_handles": len(handles),
        "handles_with_data": len(by_author),
        "authors": by_author
    }


def main():
    parser = argparse.ArgumentParser(description="Apify scraper tools (LinkedIn + X/Twitter)")
    subparsers = parser.add_subparsers(dest="command")

    scrape_cmd = subparsers.add_parser("scrape-profiles", help="Scrape LinkedIn profiles for posts")
    scrape_cmd.add_argument("--urls", required=True, help="Comma-separated LinkedIn profile URLs")

    comments_cmd = subparsers.add_parser("scrape-comments", help="Scrape LinkedIn commenting activity")
    comments_cmd.add_argument("--usernames", required=True, help="Comma-separated LinkedIn usernames (slugs)")

    tweets_cmd = subparsers.add_parser("scrape-tweets", help="Scrape recent tweets from X handles")
    tweets_cmd.add_argument("--handles", required=True, help="Comma-separated X/Twitter handles (without @)")
    tweets_cmd.add_argument("--max-per-user", type=int, default=5, help="Max tweets per user (default: 5)")

    args = parser.parse_args()
    token = load_api_key()

    if args.command == "scrape-profiles":
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]
        result = scrape_profiles(token, urls)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-comments":
        usernames = [u.strip() for u in args.usernames.split(",") if u.strip()]
        result = scrape_comments(token, usernames)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-tweets":
        handles = [h.strip().lstrip("@") for h in args.handles.split(",") if h.strip()]
        max_per = args.max_per_user
        result = scrape_tweets(token, handles, max_per)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
