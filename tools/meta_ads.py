#!/usr/bin/env python3
"""
Meta Marketing API tool for campaign management and reporting.

Usage:
    python3 tools/meta_ads.py --account-id act_XXX account-overview --days 7
    python3 tools/meta_ads.py --account-id act_XXX campaign-insights --days 7
    python3 tools/meta_ads.py --account-id act_XXX ad-insights --campaign-id 123 --days 7
    python3 tools/meta_ads.py --account-id act_XXX list-campaigns
    python3 tools/meta_ads.py --account-id act_XXX upload-image --path /path/to/image.jpg
    python3 tools/meta_ads.py --account-id act_XXX create-campaign --name "Test" --objective OUTCOME_LEADS --daily-budget 4900

Reads access token from config/api-keys.json (key: meta_access_token).
All monetary values are in cents (e.g., 4900 = $49.00).
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.ad import Ad
    from facebook_business.adobjects.adimage import AdImage
    from facebook_business.adobjects.adcreative import AdCreative
    from facebook_business.exceptions import FacebookRequestError
except ImportError:
    print("ERROR: facebook_business SDK not installed. Run: pip3 install --break-system-packages facebook_business", file=sys.stderr)
    sys.exit(1)

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"

# Standard insight fields for reporting
INSIGHT_FIELDS = [
    "campaign_name", "campaign_id",
    "adset_name", "adset_id",
    "ad_name", "ad_id",
    "spend", "impressions", "clicks", "cpc", "cpm", "ctr",
    "reach", "frequency",
    "actions", "cost_per_action_type",
    "outbound_clicks", "cost_per_outbound_click",
    "date_start", "date_stop",
]

ACCOUNT_INSIGHT_FIELDS = [
    "spend", "impressions", "clicks", "cpc", "cpm", "ctr",
    "reach", "frequency",
    "actions", "cost_per_action_type",
    "outbound_clicks", "cost_per_outbound_click",
    "date_start", "date_stop",
]


def load_access_token():
    try:
        with open(CONFIG_PATH) as f:
            keys = json.load(f)
    except FileNotFoundError:
        print("ERROR: config/api-keys.json not found", file=sys.stderr)
        sys.exit(1)

    token = keys.get("meta_access_token")
    if not token:
        print("ERROR: No meta_access_token found in config/api-keys.json. See .claude/skills/media-buyer/meta-api-setup.md", file=sys.stderr)
        sys.exit(1)
    return token


def init_api(access_token, account_id):
    """Initialize the Facebook Ads API and return an AdAccount object."""
    FacebookAdsApi.init(access_token=access_token)
    return AdAccount(account_id)


def handle_api_error(e):
    """Handle Facebook API errors with clear messages."""
    code = e.api_error_code() if hasattr(e, "api_error_code") else None
    msg = e.api_error_message() if hasattr(e, "api_error_message") else str(e)

    if code == 190:
        return {"error": "Token expired or invalid. Regenerate your access token. See .claude/skills/media-buyer/meta-api-setup.md", "code": 190}
    elif code == 32:
        return {"error": f"Rate limit hit. Wait and retry. Detail: {msg}", "code": 32}
    elif code in (10, 200):
        return {"error": f"Permission denied: {msg}. Check token scopes (ads_management, ads_read).", "code": code}
    elif code == 17:
        return {"error": f"API call limit reached. Wait a few minutes. Detail: {msg}", "code": 17}
    else:
        return {"error": f"Meta API error (code {code}): {msg}", "code": code}


def get_date_range(days):
    """Return a time_range dict for the last N days."""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return {"since": start, "until": end}


def extract_leads(actions):
    """Extract lead count from actions array."""
    if not actions:
        return 0
    for action in actions:
        if action.get("action_type") in ("lead", "offsite_conversion.fb_pixel_lead", "onsite_conversion.lead_grouped"):
            return int(action.get("value", 0))
    return 0


def extract_cpl(cost_per_action_type):
    """Extract cost per lead from cost_per_action_type array."""
    if not cost_per_action_type:
        return None
    for item in cost_per_action_type:
        if item.get("action_type") in ("lead", "offsite_conversion.fb_pixel_lead", "onsite_conversion.lead_grouped"):
            return float(item.get("value", 0))
    return None


def extract_link_clicks(outbound_clicks):
    """Extract link (outbound) click count from outbound_clicks array."""
    if not outbound_clicks:
        return None
    for item in outbound_clicks:
        if item.get("action_type") == "outbound_click":
            return int(item.get("value", 0))
    return None


def extract_cost_per_link_click(cost_per_outbound_click):
    """Extract cost per link click from cost_per_outbound_click array."""
    if not cost_per_outbound_click:
        return None
    for item in cost_per_outbound_click:
        if item.get("action_type") == "outbound_click":
            return float(item.get("value", 0))
    return None


def format_insight_row(row):
    """Format a single insight row into a clean dict."""
    actions = row.get("actions", [])
    cpat = row.get("cost_per_action_type", [])
    spend = float(row.get("spend", 0))
    leads = extract_leads(actions)
    cpl = extract_cpl(cpat)

    # Link click metrics (what Ads Manager shows as CPC)
    link_clicks = extract_link_clicks(row.get("outbound_clicks", []))
    cost_per_link_click = extract_cost_per_link_click(row.get("cost_per_outbound_click", []))

    result = {
        "spend": spend,
        "impressions": int(row.get("impressions", 0)),
        "clicks": int(row.get("clicks", 0)),
        "link_clicks": link_clicks,
        "cpc": cost_per_link_click if cost_per_link_click else (float(row.get("cpc", 0)) if row.get("cpc") else None),
        "cpm": float(row.get("cpm", 0)) if row.get("cpm") else None,
        "ctr": float(row.get("ctr", 0)) if row.get("ctr") else None,
        "reach": int(row.get("reach", 0)),
        "frequency": float(row.get("frequency", 0)) if row.get("frequency") else None,
        "leads": leads,
        "cpl": cpl if cpl else (round(spend / leads, 2) if leads > 0 else None),
        "date_start": row.get("date_start"),
        "date_stop": row.get("date_stop"),
    }

    # Add identifiers if present
    for field in ("campaign_name", "campaign_id", "adset_name", "adset_id", "ad_name", "ad_id"):
        if row.get(field):
            result[field] = row[field]

    return result


# ─── REPORTING COMMANDS ───────────────────────────────────────────────

def cmd_account_overview(account, args):
    """Account-level totals for the date range."""
    try:
        insights = account.get_insights(
            fields=ACCOUNT_INSIGHT_FIELDS,
            params={"time_range": get_date_range(args.days)},
        )
        if not insights:
            return {"message": "No data for this date range", "days": args.days}
        return format_insight_row(insights[0])
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_campaign_insights(account, args):
    """Per-campaign breakdown."""
    try:
        insights = account.get_insights(
            fields=INSIGHT_FIELDS,
            params={
                "time_range": get_date_range(args.days),
                "level": "campaign",
            },
        )
        rows = [format_insight_row(row) for row in insights]
        rows.sort(key=lambda x: x["spend"], reverse=True)
        return {"days": args.days, "campaigns": len(rows), "data": rows}
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_adset_insights(account, args):
    """Per-ad-set breakdown, optionally filtered by campaign."""
    params = {
        "time_range": get_date_range(args.days),
        "level": "adset",
    }
    if args.campaign_id:
        params["filtering"] = [{"field": "campaign.id", "operator": "EQUAL", "value": args.campaign_id}]

    try:
        insights = account.get_insights(fields=INSIGHT_FIELDS, params=params)
        rows = [format_insight_row(row) for row in insights]
        rows.sort(key=lambda x: x["spend"], reverse=True)
        return {"days": args.days, "adsets": len(rows), "data": rows}
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_ad_insights(account, args):
    """Per-ad breakdown with frequency and fatigue signals."""
    params = {
        "time_range": get_date_range(args.days),
        "level": "ad",
    }
    if args.campaign_id:
        params["filtering"] = [{"field": "campaign.id", "operator": "EQUAL", "value": args.campaign_id}]
    elif args.adset_id:
        params["filtering"] = [{"field": "adset.id", "operator": "EQUAL", "value": args.adset_id}]

    try:
        insights = account.get_insights(fields=INSIGHT_FIELDS, params=params)
        rows = []
        for row in insights:
            formatted = format_insight_row(row)
            freq = formatted.get("frequency", 0) or 0
            if freq > 5:
                formatted["fatigue"] = "CRITICAL"
            elif freq > 3:
                formatted["fatigue"] = "WARNING"
            else:
                formatted["fatigue"] = "OK"
            rows.append(formatted)
        rows.sort(key=lambda x: x["spend"], reverse=True)
        return {"days": args.days, "ads": len(rows), "data": rows}
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_creative_performance(account, args):
    """Ad-level insights enriched with creative details (image, copy, headline)."""
    params = {
        "time_range": get_date_range(args.days),
        "level": "ad",
    }
    if args.campaign_id:
        params["filtering"] = [{"field": "campaign.id", "operator": "EQUAL", "value": args.campaign_id}]

    try:
        insights = account.get_insights(fields=INSIGHT_FIELDS, params=params)
        rows = []
        for row in insights:
            formatted = format_insight_row(row)
            freq = formatted.get("frequency", 0) or 0
            formatted["fatigue"] = "CRITICAL" if freq > 5 else ("WARNING" if freq > 3 else "OK")

            # Fetch creative details for this ad
            ad_id = row.get("ad_id")
            if ad_id:
                try:
                    ad = Ad(ad_id)
                    ad_data = ad.api_get(fields=["creative"])
                    creative_id = ad_data.get("creative", {}).get("id")
                    if creative_id:
                        creative = AdCreative(creative_id)
                        creative_data = creative.api_get(fields=[
                            "body", "title", "image_url", "thumbnail_url",
                            "link_url", "call_to_action_type",
                        ])
                        formatted["creative"] = {
                            "body": creative_data.get("body"),
                            "title": creative_data.get("title"),
                            "image_url": creative_data.get("image_url") or creative_data.get("thumbnail_url"),
                            "link_url": creative_data.get("link_url"),
                            "cta": creative_data.get("call_to_action_type"),
                        }
                except Exception:
                    formatted["creative"] = None

            rows.append(formatted)

        rows.sort(key=lambda x: x["spend"], reverse=True)
        return {"days": args.days, "ads": len(rows), "data": rows}
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_daily_breakdown(account, args):
    """Day-by-day metrics for charting (spend, leads, CPL trends)."""
    params = {
        "time_range": get_date_range(args.days),
        "time_increment": 1,
    }
    if args.campaign_id:
        params["filtering"] = [{"field": "campaign.id", "operator": "EQUAL", "value": args.campaign_id}]

    try:
        insights = account.get_insights(fields=ACCOUNT_INSIGHT_FIELDS, params=params)
        rows = [format_insight_row(row) for row in insights]
        return {"days": args.days, "daily_data": rows}
    except FacebookRequestError as e:
        return handle_api_error(e)


# ─── READ COMMANDS ────────────────────────────────────────────────────

def cmd_list_campaigns(account, args):
    """List all campaigns with status and objective."""
    try:
        campaigns = account.get_campaigns(
            fields=["name", "status", "objective", "daily_budget", "lifetime_budget",
                     "start_time", "stop_time", "created_time"],
        )
        result = []
        for c in campaigns:
            result.append({
                "id": c["id"],
                "name": c.get("name"),
                "status": c.get("status"),
                "objective": c.get("objective"),
                "daily_budget": int(c["daily_budget"]) if c.get("daily_budget") else None,
                "lifetime_budget": int(c["lifetime_budget"]) if c.get("lifetime_budget") else None,
                "start_time": c.get("start_time"),
                "stop_time": c.get("stop_time"),
                "created_time": c.get("created_time"),
            })
        return {"total": len(result), "campaigns": result}
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_list_adsets(account, args):
    """List ad sets, optionally filtered by campaign."""
    try:
        params = {}
        if args.campaign_id:
            campaign = Campaign(args.campaign_id)
            adsets = campaign.get_ad_sets(
                fields=["name", "status", "daily_budget", "lifetime_budget",
                         "targeting", "optimization_goal", "billing_event", "bid_amount"],
            )
        else:
            adsets = account.get_ad_sets(
                fields=["name", "status", "daily_budget", "lifetime_budget",
                         "campaign_id", "optimization_goal", "billing_event"],
            )
        result = []
        for a in adsets:
            row = {
                "id": a["id"],
                "name": a.get("name"),
                "status": a.get("status"),
                "daily_budget": int(a["daily_budget"]) if a.get("daily_budget") else None,
                "lifetime_budget": int(a["lifetime_budget"]) if a.get("lifetime_budget") else None,
                "optimization_goal": a.get("optimization_goal"),
                "billing_event": a.get("billing_event"),
            }
            if a.get("campaign_id"):
                row["campaign_id"] = a["campaign_id"]
            if a.get("targeting"):
                row["targeting"] = a["targeting"]
            result.append(row)
        return {"total": len(result), "adsets": result}
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_list_ads(account, args):
    """List ads, optionally filtered by ad set."""
    try:
        if args.adset_id:
            adset = AdSet(args.adset_id)
            ads = adset.get_ads(fields=["name", "status", "creative", "adset_id"])
        else:
            ads = account.get_ads(fields=["name", "status", "creative", "adset_id", "campaign_id"])
        result = []
        for a in ads:
            row = {
                "id": a["id"],
                "name": a.get("name"),
                "status": a.get("status"),
                "creative_id": a.get("creative", {}).get("id") if a.get("creative") else None,
            }
            if a.get("adset_id"):
                row["adset_id"] = a["adset_id"]
            if a.get("campaign_id"):
                row["campaign_id"] = a["campaign_id"]
            result.append(row)
        return {"total": len(result), "ads": result}
    except FacebookRequestError as e:
        return handle_api_error(e)


# ─── WRITE COMMANDS ───────────────────────────────────────────────────

def cmd_create_campaign(account, args):
    """Create a campaign. Always PAUSED unless --active is passed."""
    params = {
        "name": args.name,
        "objective": args.objective,
        "status": "ACTIVE" if args.active else "PAUSED",
        "special_ad_categories": [],
    }
    if args.daily_budget:
        params["daily_budget"] = args.daily_budget
    if args.lifetime_budget:
        params["lifetime_budget"] = args.lifetime_budget
    if args.special_category:
        params["special_ad_categories"] = [args.special_category]

    try:
        campaign = account.create_campaign(params=params)
        return {
            "id": campaign["id"],
            "name": args.name,
            "status": params["status"],
            "objective": args.objective,
            "message": f"Campaign created ({"ACTIVE" if args.active else "PAUSED"})",
        }
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_create_adset(account, args):
    """Create an ad set within a campaign."""
    params = {
        "name": args.name,
        "campaign_id": args.campaign_id,
        "status": "ACTIVE" if args.active else "PAUSED",
        "optimization_goal": args.optimization_goal or "LEAD_GENERATION",
        "billing_event": "IMPRESSIONS",
    }
    if args.daily_budget:
        params["daily_budget"] = args.daily_budget
    if args.lifetime_budget:
        params["lifetime_budget"] = args.lifetime_budget
    if args.targeting:
        params["targeting"] = json.loads(args.targeting)
    else:
        # Default broad US targeting
        params["targeting"] = {
            "geo_locations": {"countries": ["US"]},
            "age_min": 25,
            "age_max": 65,
        }

    try:
        adset = account.create_ad_set(params=params)
        return {
            "id": adset["id"],
            "name": args.name,
            "campaign_id": args.campaign_id,
            "status": params["status"],
            "message": "Ad set created",
        }
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_upload_image(account, args):
    """Upload an image file and return the image hash."""
    image_path = Path(args.path)
    if not image_path.exists():
        return {"error": f"Image file not found: {args.path}"}

    try:
        image = AdImage(parent_id=account.get_id())
        image[AdImage.Field.filename] = str(image_path.resolve())
        image.remote_create()
        return {
            "hash": image[AdImage.Field.hash],
            "url": image.get(AdImage.Field.url, ""),
            "name": image_path.name,
            "message": "Image uploaded successfully",
        }
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_bulk_upload(account, args):
    """Upload multiple images and return their hashes."""
    paths = json.loads(args.paths)
    results = []
    for p in paths:
        image_path = Path(p)
        if not image_path.exists():
            results.append({"path": p, "error": "File not found"})
            continue
        try:
            image = AdImage(parent_id=account.get_id())
            image[AdImage.Field.filename] = str(image_path.resolve())
            image.remote_create()
            results.append({
                "path": p,
                "hash": image[AdImage.Field.hash],
                "url": image.get(AdImage.Field.url, ""),
                "name": image_path.name,
            })
        except FacebookRequestError as e:
            results.append({"path": p, "error": handle_api_error(e)})

    return {"total": len(results), "uploaded": sum(1 for r in results if "hash" in r), "results": results}


def cmd_create_creative(account, args):
    """Create an ad creative from an image hash and copy."""
    params = {
        "name": args.name or f"Creative {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "object_story_spec": {
            "page_id": args.page_id,
            "link_data": {
                "image_hash": args.image_hash,
                "link": args.link,
                "message": args.body,
            },
        },
    }
    if args.title:
        params["object_story_spec"]["link_data"]["name"] = args.title
    if args.description:
        params["object_story_spec"]["link_data"]["description"] = args.description
    if args.cta:
        params["object_story_spec"]["link_data"]["call_to_action"] = {
            "type": args.cta,
        }

    try:
        creative = account.create_ad_creative(params=params)
        return {
            "id": creative["id"],
            "name": params["name"],
            "message": "Creative created successfully",
        }
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_create_ad(account, args):
    """Create an ad linking a creative to an ad set. Always PAUSED unless --active."""
    params = {
        "name": args.name or f"Ad {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "adset_id": args.adset_id,
        "creative": {"creative_id": args.creative_id},
        "status": "ACTIVE" if args.active else "PAUSED",
    }

    try:
        ad = account.create_ad(params=params)
        return {
            "id": ad["id"],
            "name": params["name"],
            "adset_id": args.adset_id,
            "creative_id": args.creative_id,
            "status": params["status"],
            "message": f"Ad created ({"ACTIVE" if args.active else "PAUSED"})",
        }
    except FacebookRequestError as e:
        return handle_api_error(e)


def cmd_update_status(account, args):
    """Update the status of a campaign, ad set, or ad."""
    obj_type = args.object_type
    obj_id = args.object_id
    new_status = args.status.upper()

    if new_status not in ("ACTIVE", "PAUSED", "ARCHIVED"):
        return {"error": f"Invalid status: {new_status}. Must be ACTIVE, PAUSED, or ARCHIVED."}

    try:
        if obj_type == "campaign":
            obj = Campaign(obj_id)
        elif obj_type == "adset":
            obj = AdSet(obj_id)
        elif obj_type == "ad":
            obj = Ad(obj_id)
        else:
            return {"error": f"Invalid object type: {obj_type}. Must be campaign, adset, or ad."}

        obj.api_update(params={"status": new_status})
        return {
            "id": obj_id,
            "type": obj_type,
            "status": new_status,
            "message": f"{obj_type.capitalize()} status updated to {new_status}",
        }
    except FacebookRequestError as e:
        return handle_api_error(e)


# ─── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Meta Marketing API tool")
    parser.add_argument("--account-id", required=True, help="Ad account ID (e.g., act_123456789)")

    subparsers = parser.add_subparsers(dest="command")

    # --- Reporting ---
    overview = subparsers.add_parser("account-overview", help="Account-level totals")
    overview.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")

    camp_insights = subparsers.add_parser("campaign-insights", help="Per-campaign breakdown")
    camp_insights.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")

    adset_insights = subparsers.add_parser("adset-insights", help="Per-ad-set breakdown")
    adset_insights.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")
    adset_insights.add_argument("--campaign-id", help="Filter by campaign ID")

    ad_ins = subparsers.add_parser("ad-insights", help="Per-ad breakdown with fatigue signals")
    ad_ins.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")
    ad_ins.add_argument("--campaign-id", help="Filter by campaign ID")
    ad_ins.add_argument("--adset-id", help="Filter by ad set ID")

    creative_perf = subparsers.add_parser("creative-performance", help="Ad-level + creative details")
    creative_perf.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")
    creative_perf.add_argument("--campaign-id", help="Filter by campaign ID")

    daily = subparsers.add_parser("daily-breakdown", help="Day-by-day metrics for charting")
    daily.add_argument("--days", type=int, default=7, help="Lookback days (default: 7)")
    daily.add_argument("--campaign-id", help="Filter by campaign ID")

    # --- Read ---
    subparsers.add_parser("list-campaigns", help="List all campaigns")

    list_adsets = subparsers.add_parser("list-adsets", help="List ad sets")
    list_adsets.add_argument("--campaign-id", help="Filter by campaign ID")

    list_ads = subparsers.add_parser("list-ads", help="List ads")
    list_ads.add_argument("--adset-id", help="Filter by ad set ID")

    # --- Write ---
    create_camp = subparsers.add_parser("create-campaign", help="Create a campaign (PAUSED by default)")
    create_camp.add_argument("--name", required=True, help="Campaign name")
    create_camp.add_argument("--objective", default="OUTCOME_LEADS",
                              help="Campaign objective (default: OUTCOME_LEADS)")
    create_camp.add_argument("--daily-budget", type=int, help="Daily budget in cents (e.g., 4900 = $49)")
    create_camp.add_argument("--lifetime-budget", type=int, help="Lifetime budget in cents")
    create_camp.add_argument("--special-category", help="Special ad category (e.g., HOUSING, CREDIT)")
    create_camp.add_argument("--active", action="store_true", help="Create as ACTIVE (default: PAUSED)")

    create_as = subparsers.add_parser("create-adset", help="Create an ad set")
    create_as.add_argument("--name", required=True, help="Ad set name")
    create_as.add_argument("--campaign-id", required=True, help="Parent campaign ID")
    create_as.add_argument("--daily-budget", type=int, help="Daily budget in cents")
    create_as.add_argument("--lifetime-budget", type=int, help="Lifetime budget in cents")
    create_as.add_argument("--targeting", help="Targeting JSON string")
    create_as.add_argument("--optimization-goal", help="Optimization goal (default: LEAD_GENERATION)")
    create_as.add_argument("--active", action="store_true", help="Create as ACTIVE (default: PAUSED)")

    upload = subparsers.add_parser("upload-image", help="Upload an image")
    upload.add_argument("--path", required=True, help="Path to image file")

    bulk = subparsers.add_parser("bulk-upload", help="Upload multiple images")
    bulk.add_argument("--paths", required=True, help="JSON array of image paths")

    create_cr = subparsers.add_parser("create-creative", help="Create an ad creative")
    create_cr.add_argument("--name", help="Creative name")
    create_cr.add_argument("--image-hash", required=True, help="Image hash from upload")
    create_cr.add_argument("--body", required=True, help="Primary text / message")
    create_cr.add_argument("--title", help="Headline")
    create_cr.add_argument("--description", help="Description text")
    create_cr.add_argument("--link", required=True, help="Destination URL")
    create_cr.add_argument("--page-id", required=True, help="Facebook Page ID")
    create_cr.add_argument("--cta", help="Call to action type (e.g., LEARN_MORE, SIGN_UP, GET_QUOTE)")

    create_ad = subparsers.add_parser("create-ad", help="Create an ad (PAUSED by default)")
    create_ad.add_argument("--name", help="Ad name")
    create_ad.add_argument("--adset-id", required=True, help="Parent ad set ID")
    create_ad.add_argument("--creative-id", required=True, help="Creative ID")
    create_ad.add_argument("--active", action="store_true", help="Create as ACTIVE (default: PAUSED)")

    update = subparsers.add_parser("update-status", help="Update status of campaign/adset/ad")
    update.add_argument("--object-type", required=True, choices=["campaign", "adset", "ad"])
    update.add_argument("--object-id", required=True, help="ID of the object to update")
    update.add_argument("--status", required=True, help="New status: ACTIVE, PAUSED, or ARCHIVED")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    access_token = load_access_token()
    account = init_api(access_token, args.account_id)

    commands = {
        "account-overview": cmd_account_overview,
        "campaign-insights": cmd_campaign_insights,
        "adset-insights": cmd_adset_insights,
        "ad-insights": cmd_ad_insights,
        "creative-performance": cmd_creative_performance,
        "daily-breakdown": cmd_daily_breakdown,
        "list-campaigns": cmd_list_campaigns,
        "list-adsets": cmd_list_adsets,
        "list-ads": cmd_list_ads,
        "create-campaign": cmd_create_campaign,
        "create-adset": cmd_create_adset,
        "upload-image": cmd_upload_image,
        "bulk-upload": cmd_bulk_upload,
        "create-creative": cmd_create_creative,
        "create-ad": cmd_create_ad,
        "update-status": cmd_update_status,
    }

    handler = commands.get(args.command)
    if handler:
        result = handler(account, args)
        print(json.dumps(result, indent=2, default=str))
        if isinstance(result, dict) and "error" in result:
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
