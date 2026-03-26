#!/usr/bin/env python3
"""Meta Ads Dashboard - Local interactive dashboard for daily campaign management.

Usage:
    python3 tools/dashboard/app.py

Opens at http://localhost:5050
"""

import argparse
import json
import sys
from pathlib import Path

# Add tools/ to path so we can import meta_ads
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify

import meta_ads
from config import ACCOUNTS, DEFAULT_DAYS, PORT
from insights import generate_insights

app = Flask(__name__)


# --- Helpers ---

class MockArgs:
    """Mock argparse.Namespace to call meta_ads cmd_* functions."""
    def __init__(self, **kwargs):
        self.days = kwargs.get("days", DEFAULT_DAYS)
        self.campaign_id = kwargs.get("campaign_id", None)
        self.adset_id = kwargs.get("adset_id", None)


def init_account(account_id):
    """Initialize Meta API and return an AdAccount object."""
    token = meta_ads.load_access_token()
    return meta_ads.init_api(token, account_id)


def fetch_dashboard_data(account_id, days):
    """Fetch all data needed for the main dashboard.

    Keeps it fast: no creative-performance calls on the main page.
    """
    account = init_account(account_id)
    args = MockArgs(days=days)

    # Core data only - 4 API calls, no creative detail fetching
    overview = meta_ads.cmd_account_overview(account, args)
    if "error" in overview:
        return {"error": overview["error"], "code": overview.get("code")}

    campaign_insights = meta_ads.cmd_campaign_insights(account, args)
    campaign_list = meta_ads.cmd_list_campaigns(account, args)
    ad_data = meta_ads.cmd_ad_insights(account, args)
    daily = meta_ads.cmd_daily_breakdown(account, args)

    # Build campaign budget/status lookup
    budget_map = {}
    status_map = {}
    if "campaigns" in campaign_list:
        for c in campaign_list["campaigns"]:
            budget_map[c["id"]] = c.get("daily_budget")
            status_map[c["id"]] = c.get("status")

    # Merge insights with metadata
    campaigns = []
    if "data" in campaign_insights:
        for c in campaign_insights["data"]:
            cid = c.get("campaign_id")
            c["daily_budget"] = budget_map.get(cid)
            c["campaign_status"] = status_map.get(cid)
            campaigns.append(c)

    ads = ad_data.get("data", []) if isinstance(ad_data, dict) else []
    daily_data = daily.get("daily_data", []) if isinstance(daily, dict) else []

    # Generate insights
    expert_insights = generate_insights(
        overview, campaigns, ads, daily_data, account_id, days
    )

    return {
        "account_id": account_id,
        "account_name": ACCOUNTS.get(account_id, {}).get("name", account_id),
        "days": days,
        "summary": overview,
        "campaigns": campaigns,
        "ads": ads,
        "daily_data": daily_data,
        "insights": expert_insights,
    }


def fetch_campaign_data(account_id, campaign_id, days):
    """Fetch data for a single campaign drill-down.

    Creative details fetched here (scoped to one campaign, so fast enough).
    """
    account = init_account(account_id)
    args = MockArgs(days=days, campaign_id=campaign_id)

    ad_data = meta_ads.cmd_ad_insights(account, args)
    daily = meta_ads.cmd_daily_breakdown(account, args)
    creative_data = meta_ads.cmd_creative_performance(account, args)

    # Get campaign-level summary
    overview_args = MockArgs(days=days)
    campaign_insights = meta_ads.cmd_campaign_insights(account, overview_args)

    campaign_summary = None
    if "data" in campaign_insights:
        for c in campaign_insights["data"]:
            if c.get("campaign_id") == campaign_id:
                campaign_summary = c
                break

    ads = ad_data.get("data", []) if isinstance(ad_data, dict) else []
    creatives = creative_data.get("data", []) if isinstance(creative_data, dict) else []
    daily_data = daily.get("daily_data", []) if isinstance(daily, dict) else []

    # Campaign-specific insights
    insights = generate_insights(
        campaign_summary or {}, [campaign_summary] if campaign_summary else [],
        ads, daily_data, account_id, days
    )

    return {
        "account_id": account_id,
        "account_name": ACCOUNTS.get(account_id, {}).get("name", account_id),
        "campaign_id": campaign_id,
        "campaign_name": (campaign_summary or {}).get("campaign_name", "Unknown"),
        "days": days,
        "summary": campaign_summary or {},
        "ads": ads,
        "creatives": creatives,
        "daily_data": daily_data,
        "insights": insights,
    }


# --- Routes ---

@app.route("/")
def index():
    """Main dashboard page."""
    account_id = request.args.get("account", list(ACCOUNTS.keys())[0])
    days = int(request.args.get("days", DEFAULT_DAYS))

    try:
        data = fetch_dashboard_data(account_id, days)
    except SystemExit:
        data = {"error": "Meta API token not configured. See .claude/skills/media-buyer/meta-api-setup.md"}
    except Exception as e:
        data = {"error": str(e)}

    return render_template("index.html",
                           data=data,
                           accounts=ACCOUNTS,
                           current_account=account_id,
                           current_days=days,
                           data_json=json.dumps(data, default=str))


@app.route("/campaign/<campaign_id>")
def campaign_detail(campaign_id):
    """Campaign drill-down page."""
    account_id = request.args.get("account", list(ACCOUNTS.keys())[0])
    days = int(request.args.get("days", DEFAULT_DAYS))

    try:
        data = fetch_campaign_data(account_id, campaign_id, days)
    except SystemExit:
        data = {"error": "Meta API token not configured."}
    except Exception as e:
        data = {"error": str(e)}

    return render_template("campaign.html",
                           data=data,
                           accounts=ACCOUNTS,
                           current_account=account_id,
                           current_days=days,
                           data_json=json.dumps(data, default=str))


@app.route("/api/data")
def api_data():
    """JSON endpoint for AJAX refresh."""
    account_id = request.args.get("account", list(ACCOUNTS.keys())[0])
    days = int(request.args.get("days", DEFAULT_DAYS))

    try:
        data = fetch_dashboard_data(account_id, days)
    except SystemExit:
        return jsonify({"error": "Meta API token not configured."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)


@app.route("/api/campaign/<campaign_id>")
def api_campaign(campaign_id):
    """JSON endpoint for campaign drill-down refresh."""
    account_id = request.args.get("account", list(ACCOUNTS.keys())[0])
    days = int(request.args.get("days", DEFAULT_DAYS))

    try:
        data = fetch_campaign_data(account_id, campaign_id, days)
    except SystemExit:
        return jsonify({"error": "Meta API token not configured."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)


@app.route("/api/accounts")
def api_accounts():
    """List configured accounts."""
    return jsonify(ACCOUNTS)


if __name__ == "__main__":
    print(f"\n  Meta Ads Dashboard running at http://localhost:{PORT}\n")
    app.run(host="127.0.0.1", port=PORT, debug=False)
