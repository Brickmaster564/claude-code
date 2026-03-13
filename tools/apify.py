#!/usr/bin/env python3
"""
Apify scraper tools (LinkedIn + X/Twitter + Instagram).

Usage:
    python3 tools/apify.py scrape-profiles --urls "https://linkedin.com/in/person1,https://linkedin.com/in/person2"
    python3 tools/apify.py scrape-comments --usernames "person1,person2"
    python3 tools/apify.py scrape-tweets --handles "sabrisuby,TheJeremyHaynes" [--max-per-user 5]
    python3 tools/apify.py scrape-instagram-related --handles "mikethurstonfitness,lewishowes" [--min-followers 100000]
    python3 tools/apify.py scrape-instagram-profile --handles "mikethurstonfitness,lewishowes"
    python3 tools/apify.py scrape-company-employees --company-url "https://linkedin.com/company/goldco/" [--job-title "marketing"] [--max-employees 5]

scrape-profiles:            LinkedIn profile data including recent posts.
scrape-comments:            LinkedIn commenting activity.
scrape-tweets:              Recent tweets from X handles.
scrape-instagram-related:   Suggested/related Instagram profiles (filtered by follower count).
scrape-instagram-profile:   Instagram profile details (followers, bio, verified status).
scrape-company-employees:   LinkedIn company employees (no cookies). ~$0.01-0.05/run.

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
ACTOR_INSTAGRAM_RELATED = "scrapio~instagram-related-person-scraper"
ACTOR_INSTAGRAM_PROFILE = "shu8hvrXbJbY3Eb9W"
ACTOR_COMPANY_EMPLOYEES = "apimaestro~linkedin-company-employees-scraper-no-cookies"
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


def scrape_comments(token, usernames, results_per_profile=1):
    """Scrape LinkedIn commenting activity for given usernames (batched, up to 50 per run)."""
    if not usernames:
        return {"error": "No usernames provided"}

    BATCH_SIZE = 50
    all_items = []

    for i in range(0, len(usernames), BATCH_SIZE):
        batch = usernames[i:i + BATCH_SIZE]
        actor_input = {
            "usernames": batch,
            "limit": results_per_profile
        }
        raw = run_actor(token, ACTOR_COMMENTS, actor_input,
                        label=f"comments batch {i // BATCH_SIZE + 1} ({len(batch)} profiles)")
        if isinstance(raw, dict) and "error" in raw:
            print(f"Warning: batch {i // BATCH_SIZE + 1} failed: {raw['error']}", file=sys.stderr)
            continue
        batch_items = raw if isinstance(raw, list) else []
        all_items.extend(batch_items)

    items = all_items

    # Group comments by profile username
    import datetime
    by_user = {u.lower(): [] for u in usernames}
    for c in items:
        profile_id = (c.get("source_profile", "") or c.get("profileUsername", "")
                      or c.get("username", "")).lower()
        if profile_id in by_user:
            by_user[profile_id].append(c)

    results = {"total": 0, "active_commenters": 0, "inactive": 0, "profiles": []}

    for username in usernames:
        comments = by_user.get(username.lower(), [])
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

        has_recent = False
        if most_recent_ts > 0:
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


def scrape_tweets(token, handles, max_per_user=3):
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


def scrape_instagram_related(token, handles, min_followers=100000):
    """Scrape Instagram suggested/related profiles for given handles."""
    if not handles:
        return {"error": "No handles provided"}

    # Build profile URLs from handles
    profile_urls = [f"https://www.instagram.com/{h.strip('/')}/" for h in handles]

    actor_input = {
        "profiles": profile_urls,
        "resultsLimit": 20
    }

    raw = run_actor(token, ACTOR_INSTAGRAM_RELATED, actor_input,
                    label=f"related profiles for {len(handles)} handles")
    if isinstance(raw, dict) and "error" in raw:
        return raw

    items = raw if isinstance(raw, list) else []

    profiles = []
    for item in items:
        followers = item.get("followersCount", 0) or item.get("followers", 0) or 0
        profile = {
            "username": item.get("username", "") or item.get("userName", ""),
            "full_name": item.get("fullName", "") or item.get("full_name", ""),
            "bio": (item.get("biography", "") or item.get("bio", "") or "")[:200],
            "followers": followers,
            "profile_url": f"https://www.instagram.com/{item.get('username', '')}/"
        }
        profiles.append(profile)

    filtered = [p for p in profiles if p["followers"] >= min_followers]

    return {
        "total_found": len(profiles),
        "filtered_by_followers": len(filtered),
        "min_followers_threshold": min_followers,
        "profiles": filtered
    }


def scrape_instagram_profile(token, handles):
    """Scrape Instagram profile details for given handles."""
    if not handles:
        return {"error": "No handles provided"}

    actor_input = {
        "usernames": handles,
        "resultsType": "details"
    }

    raw = run_actor(token, ACTOR_INSTAGRAM_PROFILE, actor_input,
                    label=f"profiles for {len(handles)} handles")
    if isinstance(raw, dict) and "error" in raw:
        return raw

    items = raw if isinstance(raw, list) else []

    profiles = []
    for item in items:
        profiles.append({
            "username": item.get("username", "") or item.get("userName", ""),
            "full_name": item.get("fullName", "") or item.get("full_name", ""),
            "bio": (item.get("biography", "") or item.get("bio", "") or "")[:200],
            "followers": item.get("followersCount", 0) or item.get("followers", 0) or 0,
            "following": item.get("followingCount", 0) or item.get("following", 0) or 0,
            "posts": item.get("postsCount", 0) or item.get("posts", 0) or 0,
            "verified": item.get("verified", False) or item.get("isVerified", False),
            "profile_url": f"https://www.instagram.com/{item.get('username', '')}/"
        })

    return {
        "total": len(profiles),
        "profiles": profiles
    }


def scrape_company_employees(token, company_url, job_title="", max_employees=5):
    """Scrape LinkedIn company employees. No cookies required.

    Args:
        company_url: LinkedIn company URL (e.g. https://www.linkedin.com/company/goldco/)
        job_title: Optional filter keyword (e.g. "marketing", "business development")
        max_employees: Max results to return (default 5, keeps cost ~$0.01-0.05)
    """
    if not company_url:
        return {"error": "No company URL provided"}

    actor_input = {
        "identifier": company_url.rstrip("/") + "/",
        "max_employees": max_employees
    }
    if job_title:
        actor_input["job_title"] = job_title

    company_name = company_url.rstrip("/").split("/")[-1]
    raw = run_actor(token, ACTOR_COMPANY_EMPLOYEES, actor_input,
                    label=f"employees at {company_name} (filter: {job_title or 'none'})")
    if isinstance(raw, dict) and "error" in raw:
        return raw

    items = raw if isinstance(raw, list) else []

    employees = []
    for item in items:
        employees.append({
            "fullname": item.get("fullname", ""),
            "first_name": item.get("first_name", ""),
            "last_name": item.get("last_name", ""),
            "headline": item.get("headline", ""),
            "profile_url": item.get("profile_url", ""),
            "location": item.get("location", {}).get("full", ""),
            "public_identifier": item.get("public_identifier", "")
        })

    return {
        "company_url": company_url,
        "job_title_filter": job_title,
        "total": len(employees),
        "employees": employees
    }


def main():
    parser = argparse.ArgumentParser(description="Apify scraper tools (LinkedIn + X/Twitter + Instagram)")
    subparsers = parser.add_subparsers(dest="command")

    scrape_cmd = subparsers.add_parser("scrape-profiles", help="Scrape LinkedIn profiles for posts")
    scrape_cmd.add_argument("--urls", required=True, help="Comma-separated LinkedIn profile URLs")

    comments_cmd = subparsers.add_parser("scrape-comments", help="Scrape LinkedIn commenting activity")
    comments_cmd.add_argument("--usernames", required=True, help="Comma-separated LinkedIn usernames (slugs)")
    comments_cmd.add_argument("--results-per-profile", type=int, default=1, help="Max comments per profile (default: 1)")

    tweets_cmd = subparsers.add_parser("scrape-tweets", help="Scrape recent tweets from X handles")
    tweets_cmd.add_argument("--handles", required=True, help="Comma-separated X/Twitter handles (without @)")
    tweets_cmd.add_argument("--max-per-user", type=int, default=3, help="Max tweets per user (default: 3)")

    ig_related_cmd = subparsers.add_parser("scrape-instagram-related", help="Scrape Instagram suggested/related profiles")
    ig_related_cmd.add_argument("--handles", required=True, help="Comma-separated Instagram handles (without @)")
    ig_related_cmd.add_argument("--min-followers", type=int, default=100000, help="Min followers to include (default: 100000)")

    ig_profile_cmd = subparsers.add_parser("scrape-instagram-profile", help="Scrape Instagram profile details")
    ig_profile_cmd.add_argument("--handles", required=True, help="Comma-separated Instagram handles (without @)")

    employees_cmd = subparsers.add_parser("scrape-company-employees", help="Scrape LinkedIn company employees (no cookies)")
    employees_cmd.add_argument("--company-url", required=True, help="LinkedIn company URL")
    employees_cmd.add_argument("--job-title", default="", help="Job title filter keyword (e.g. 'marketing')")
    employees_cmd.add_argument("--max-employees", type=int, default=5, help="Max employees to return (default: 5)")

    args = parser.parse_args()
    token = load_api_key()

    if args.command == "scrape-profiles":
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]
        result = scrape_profiles(token, urls)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-comments":
        usernames = [u.strip() for u in args.usernames.split(",") if u.strip()]
        result = scrape_comments(token, usernames, args.results_per_profile)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-tweets":
        handles = [h.strip().lstrip("@") for h in args.handles.split(",") if h.strip()]
        max_per = args.max_per_user
        result = scrape_tweets(token, handles, max_per)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-instagram-related":
        handles = [h.strip().lstrip("@") for h in args.handles.split(",") if h.strip()]
        result = scrape_instagram_related(token, handles, args.min_followers)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-instagram-profile":
        handles = [h.strip().lstrip("@") for h in args.handles.split(",") if h.strip()]
        result = scrape_instagram_profile(token, handles)
        print(json.dumps(result, indent=2))
    elif args.command == "scrape-company-employees":
        result = scrape_company_employees(token, args.company_url, args.job_title, args.max_employees)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
