#!/usr/bin/env python3
"""
Cashflow operational expenses auto-sync.

Pulls Revolut card payments for the current month, matches them against the
operational expenses section of the cashflow master sheet, updates existing
rows, and inserts new rows for unrecognised tools.

Usage:
  python3 tools/cashflow_sync.py [--month YYYY-MM] [--dry-run]
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests as http_requests

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"

SHEET_ID = "1JGkLHMHdur-faQysThO1cvTa4SbtT7dYojPbBLtsq9o"
TAB_NAME = "2026"
TAB_ID = 522278131
NCOLS = 26

BLUE_L = {"red": 0.890, "green": 0.949, "blue": 0.992}

# ── Skip list — these Revolut merchants are NOT operational subscriptions ─────
# Any merchant whose normalized name CONTAINS one of these keywords is skipped.
SKIP_KEYWORDS = [
    # Food & drink
    "tesco", "sainsbury", "waitrose", "lidl", "aldi", "boots",
    "farmer j", "blank street", "rondo", "hideaway", "coffee",
    "restaurant", "kitchen", "cafe", "bar", "pub",
    "kyoto", "boathouse", "back to roots", "1970", "beach club",
    # Travel
    "uber", "deliveroo", "bolt", "ryde", "taxi", "transporte",
    "hotel", "hilton", "marriott", "ibis", "grosvenor", "25hours",
    "airways", "ryanair", "emirates", "easyjet", "flight",
    "ssp uk",
    # Physical / one-off retail
    "currys", "argos",
    # Government / tax / compliance
    "government", "jersey", "social security", "hmrc",
    "office of the informat",  # ICO registration
    # Payment processors / FX
    "payoneer", "wise", "transferwise", "exchanged",
    # Revolut own fees
    "expenses app", "company pro plan",
    # Freelancers / staff (ad-hoc payments)
    "maciekdesign", "pmanhtuan", "hshefins", "hgumidala",
    "veljes", "abdommdouh", "gyurky", "gtaha", "zak editing",
    "connectcentre", "salman",
    # Ad spend (tracked separately)
    "uproas",
]

# Merchants that are transfers (not card payments) — handled by type filter
# but added here as a safety net
SKIP_STARTS_WITH = ["to "]

# ── Aliases: normalized Revolut name fragment → normalized sheet label ────────
# First matching alias wins.
ALIASES = [
    ("apollo.io",         "apollo"),
    ("meta pay",          "meta"),
    ("openai",            "gpt"),
    ("anthropic",         "claude"),
    ("google workspace",  "google workspace"),
    ("gettrackify",       "go high level"),
    ("miro.com",          "miro"),
    ("wispr",             "wispr systems"),
    ("higgsfield",        "higgsfield"),
    ("landerlab",         "landerlab"),
    ("clientup",          "clientup"),
    ("lemon squeezy",     "clickflare"),
    ("nordvpn",           "nordvpn"),
    ("1of10",             "1of10"),
    ("hemingway",         "hemingway editor"),
    ("adspow",            "adspower"),
    ("myprivate",         "myprivateproxy"),
    ("oxylabs",           "oxylabs"),
    ("floxy",             "floxy"),
    ("perplexity",        "perplexity"),
    ("namecheap",         "namecheap"),
    ("number api",        "number api"),
    ("skool",             "skool"),
    ("favikon",           "favikon"),
    ("blotato",           "blotato"),
    ("gethookd",          "gethookd"),
    ("auphonic",          "auphonic"),
    ("beehiiv",           "beehiiv (ftt)"),
    ("airtable",          "airtable"),
    ("apify",             "apify"),
    ("dropbox",           "dropbox"),
    ("asana",             "asana"),
    ("lemlist",           "lemlist"),
    ("vizard",            "vizard"),
    ("notion",            "notion"),
    ("slack",             "slack"),
    ("linkedin",          "linkedin"),
    ("riverside",         "riverside"),
    ("adobe",             "adobe"),
    ("heygen",            "heygen"),
    ("instantly",         "instantly"),
    ("calendly",          "calendly"),
    ("webflow",           "webflow"),
    ("veed",              "veed"),
    ("zoom",              "zoom"),
    ("framer",            "framer"),
    ("make",              "make"),
    ("twitter",           "x sub"),
    ("manychat",          "manychat"),
    ("remini",            "remini ai"),
    ("clickflare",        "clickflare"),
    ("adspower",          "adspower"),
    ("notta",             "notta"),
    ("buffer",            "buffer"),
    ("listkit",           "listkit"),
    ("contactout",        "contactout"),
    ("paddle",            "paddle"),
    ("dumpling",          "dumpling ai"),
]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower().strip())


def should_skip(merchant: str) -> bool:
    n = norm(merchant)
    if any(n.startswith(p) for p in SKIP_STARTS_WITH):
        return True
    return any(kw in n for kw in SKIP_KEYWORDS)


def alias_match(merchant: str) -> str | None:
    """Return the normalized sheet label this merchant maps to, or None."""
    n = norm(merchant)
    for fragment, target in ALIASES:
        if fragment in n:
            return target
    return None


def label_match(merchant: str, sheet_labels: list[str]) -> str | None:
    """Find the best matching sheet row label for a Revolut merchant name."""
    if should_skip(merchant):
        return "__skip__"

    # Check alias table first
    alias = alias_match(merchant)

    # Try to find matching sheet label
    for label in sheet_labels:
        ln = norm(label)
        if not ln:
            continue
        # Direct fuzzy
        mn = norm(merchant)
        if ln == mn or ln in mn or mn in ln:
            return label
        # Alias match
        if alias and (alias == ln or alias in ln):
            return label

    # Alias resolves to a name not yet in sheet → will become a new row
    if alias:
        return f"__new__{alias}"

    # No match and not in skip list → flag as potential new item if it looks
    # like a subscription (amount filter applied by caller)
    return None


# ── Google Sheets helpers ─────────────────────────────────────────────────────

def get_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    with open(CONFIG_DIR / "google-token-nalu.json") as f:
        token = json.load(f)
    with open(CONFIG_DIR / "google-credentials-nalu.json") as f:
        creds_data = json.load(f)
    installed = creds_data.get("installed") or creds_data.get("web")
    creds = Credentials(
        token=token.get("token"),
        refresh_token=token.get("refresh_token"),
        token_uri=installed["token_uri"],
        client_id=installed["client_id"],
        client_secret=installed["client_secret"],
    )
    if creds.expired:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)


def read_sheet(service) -> list[list[str]]:
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1:Z220",
    ).execute()
    return result.get("values", [])


def find_month_col(rows: list, month_str: str) -> int:
    """Return 0-based column index for the given month ('2026-03')."""
    dt = datetime.strptime(month_str, "%Y-%m")
    header = dt.strftime("%b-%y")  # 'Mar-26'
    for row in rows[:15]:
        for ci, cell in enumerate(row):
            if cell.strip() == header:
                return ci
    raise ValueError(f"Month header '{header}' not found in sheet")


def find_opex_bounds(rows: list) -> tuple[int, int, int]:
    """
    Return (subs_row_1idx, general_row_1idx, total_opex_row_1idx).
    All 1-indexed.
    """
    subs_row = general_row = total_row = None
    for i, row in enumerate(rows):
        cell = row[0].strip() if row else ""
        cell_b = row[1].strip() if len(row) > 1 else ""
        stripped = cell.rstrip()
        if stripped in ("Subscriptions", "Subscriptions "):
            subs_row = i + 1
        if stripped == "General":
            general_row = i + 1
        if "Total Op Expenses" in cell_b or "Total Op Expenses" in cell:
            total_row = i + 1
    return subs_row, general_row, total_row


def read_opex_labels(rows: list, subs_row: int, general_row: int) -> dict:
    """
    Return {norm_label: {'row': int_1idx, 'label': str}} for all rows
    in the subscriptions section (between subs_row and general_row).
    """
    result = {}
    for i in range(subs_row, general_row - 1):
        row = rows[i] if i < len(rows) else []
        cell = row[0].strip() if row else ""
        if cell and cell not in ("Subscriptions", "Subscriptions "):
            result[norm(cell)] = {"row": i + 1, "label": cell}
    return result


# ── Revolut helpers ───────────────────────────────────────────────────────────

def get_revolut_totals(month_str: str) -> dict[str, float]:
    """Return {merchant_name: total_gbp} for card payments in the month."""
    import subprocess
    from calendar import monthrange

    year, month = int(month_str[:4]), int(month_str[5:])
    last_day = monthrange(year, month)[1]

    result = subprocess.run(
        [
            "python3", str(BASE_DIR / "tools" / "revolut.py"),
            "transactions",
            "--from", f"{month_str}-01",
            "--to", f"{month_str}-{last_day:02d}",
            "--limit", "500",
            "--json",
        ],
        capture_output=True, text=True, cwd=str(BASE_DIR),
    )
    if result.returncode != 0:
        print(f"Revolut error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    txns = json.loads(result.stdout)
    totals: dict[str, float] = defaultdict(float)

    for t in txns:
        if t.get("state") not in ("completed", "pending"):
            continue
        if t.get("type") != "card_payment":
            continue
        leg = t["legs"][0]
        amount = leg.get("amount", 0)
        if amount >= 0:
            continue
        merchant = (t.get("merchant", {}) or {}).get("name") or leg.get("description", "")
        if not merchant:
            continue
        totals[merchant] += abs(amount)

    return dict(totals)


# ── Main sync ─────────────────────────────────────────────────────────────────

def run_sync(month_str: str, dry_run: bool = False):
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Cashflow sync — {month_str}")
    print("=" * 50)

    service = get_service()
    rows = read_sheet(service)
    month_col = find_month_col(rows, month_str)
    subs_row, general_row, total_opex_row = find_opex_bounds(rows)

    if not subs_row or not general_row:
        print("ERROR: Could not find Subscriptions / General section boundaries.", file=sys.stderr)
        sys.exit(1)

    print(f"Sheet: Subscriptions start row {subs_row}, General row {general_row}, month col {month_col} ({chr(65+month_col)})")

    # Read existing opex labels
    label_map = read_opex_labels(rows, subs_row, general_row)
    sheet_labels = [v["label"] for v in label_map.values()]

    # Pull Revolut totals
    revolut_totals = get_revolut_totals(month_str)
    print(f"Revolut: {len(revolut_totals)} card payment merchants found")

    # Consolidate Google Workspace variants
    gws_total = 0.0
    gws_keys = [k for k in revolut_totals if "google workspace" in k.lower()]
    for k in gws_keys:
        gws_total += revolut_totals.pop(k)
    if gws_total:
        revolut_totals["Google Workspace"] = gws_total

    # Consolidate Beehiiv variants (FTT + DV separate rows handled below)
    # Leave as-is since sheet has distinct Beehiiv rows

    # Match merchants
    updates = []   # (row_1idx, col_idx, new_val, old_val, label)
    new_items = [] # (display_name, amount)
    skipped = []
    unmatched = []

    for merchant, total_gbp in sorted(revolut_totals.items(), key=lambda x: -x[1]):
        rounded = round(total_gbp)
        if rounded < 3:
            continue  # Ignore trivial amounts

        matched_label = label_match(merchant, sheet_labels)

        if matched_label == "__skip__":
            skipped.append(merchant)
            continue

        if matched_label and not matched_label.startswith("__new__"):
            # Existing row — check if value needs updating
            row_info = label_map.get(norm(matched_label))
            if not row_info:
                # Try partial match
                for k, v in label_map.items():
                    if k in norm(matched_label) or norm(matched_label) in k:
                        row_info = v
                        break
            if row_info:
                row_num = row_info["row"]
                # Get current sheet value
                sheet_row = rows[row_num - 1] if row_num <= len(rows) else []
                current_raw = sheet_row[month_col].strip() if month_col < len(sheet_row) else ""
                current_val = int(re.sub(r"[^\d]", "", current_raw)) if re.search(r"\d", current_raw) else 0

                if rounded != current_val:
                    updates.append({
                        "row": row_num,
                        "col": month_col,
                        "new_val": rounded,
                        "old_val": current_val,
                        "label": row_info["label"],
                    })
                continue

        if matched_label and matched_label.startswith("__new__"):
            display = matched_label[7:].title()  # strip '__new__' prefix
            new_items.append((display, rounded))
            continue

        # No alias match — check if it looks like a subscription (recurring small amount)
        # Only flag if amount is in subscription range
        if 3 <= rounded <= 500:
            unmatched.append((merchant, rounded))

    # Treat unmatched as new items (operator can clean up)
    new_items.extend(unmatched)

    # Deduplicate new_items by normalized name
    seen_new = set()
    deduped_new = []
    for name, amt in new_items:
        key = norm(name)
        if key not in seen_new:
            seen_new.add(key)
            deduped_new.append((name, amt))
    new_items = deduped_new

    # ── Report ──────────────────────────────────────────────────────────────
    print(f"\nUpdates ({len(updates)}):")
    for u in updates:
        print(f"  Row {u['row']} {u['label']}: {u['old_val']} → {u['new_val']}")

    print(f"\nNew items ({len(new_items)}):")
    for name, amt in new_items:
        print(f"  {name}: {amt}")

    print(f"\nSkipped: {len(skipped)} non-subscription merchants")

    if dry_run:
        print("\n[DRY RUN] No changes written.")
        return

    if not updates and not new_items:
        print("\nSheet is already up to date.")
        _send_slack(month_str, [], [], 0)
        return

    # ── Apply updates ────────────────────────────────────────────────────────
    if updates:
        col_letter = chr(65 + month_col)
        batch_data = []
        for u in updates:
            batch_data.append({
                "range": f"{TAB_NAME}!{col_letter}{u['row']}",
                "values": [[u["new_val"]]],
            })
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": batch_data},
        ).execute()
        print(f"\nWrote {len(updates)} updates.")

    # ── Insert new rows ──────────────────────────────────────────────────────
    # Re-read sheet to get current general_row (may have shifted if user added rows)
    rows = read_sheet(service)
    _, general_row, _ = find_opex_bounds(rows)

    if new_items:
        insert_requests = []
        # Insert all rows in one go at general_row - 1 (above General header)
        insert_idx = general_row - 2  # 0-based, above the empty row before General

        # Insert N blank rows above that position (bottom to top doesn't matter for a
        # single insertDimension block)
        insert_requests.append({
            "insertDimension": {
                "range": {
                    "sheetId": TAB_ID,
                    "dimension": "ROWS",
                    "startIndex": insert_idx,
                    "endIndex": insert_idx + len(new_items),
                },
                "inheritFromBefore": True,
            }
        })
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID, body={"requests": insert_requests}
        ).execute()

        # Write labels and values
        col_letter = chr(65 + month_col)
        batch_data = []
        for offset, (name, amt) in enumerate(new_items):
            row_num = insert_idx + 1 + offset  # 1-indexed after insertion
            batch_data.append({"range": f"{TAB_NAME}!A{row_num}", "values": [[name]]})
            batch_data.append({"range": f"{TAB_NAME}!{col_letter}{row_num}", "values": [[amt]]})

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": batch_data},
        ).execute()

        # Apply blue-light formatting to new rows
        fmt_requests = [{
            "repeatCell": {
                "range": {
                    "sheetId": TAB_ID,
                    "startRowIndex": insert_idx,
                    "endRowIndex": insert_idx + len(new_items),
                    "startColumnIndex": 0,
                    "endColumnIndex": NCOLS,
                },
                "cell": {"userEnteredFormat": {"backgroundColor": BLUE_L}},
                "fields": "userEnteredFormat(backgroundColor)",
            }
        }]
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID, body={"requests": fmt_requests}
        ).execute()
        print(f"Inserted {len(new_items)} new rows above General section.")

    _send_slack(month_str, updates, new_items, len(skipped))
    print("\nDone.")


def _send_slack(month_str: str, updates: list, new_items: list, skipped_count: int):
    try:
        import subprocess
        dt = datetime.strptime(month_str, "%Y-%m")
        month_label = dt.strftime("%B %Y")

        lines = [f"*Cashflow sync complete — {month_label}*"]

        if updates:
            lines.append(f"\n*Updated {len(updates)} existing rows:*")
            for u in updates:
                diff = u["new_val"] - u["old_val"]
                sign = "+" if diff > 0 else ""
                lines.append(f"  • {u['label']}: £{u['old_val']} → £{u['new_val']} ({sign}£{diff})")

        if new_items:
            lines.append(f"\n*Added {len(new_items)} new rows:*")
            for name, amt in new_items:
                lines.append(f"  • {name}: £{amt}")

        if not updates and not new_items:
            lines.append("No changes — sheet already matches Revolut.")

        lines.append(f"\n_Sheet: <https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit|Open cashflow>_")

        message = "\n".join(lines)

        result = subprocess.run(
            ["python3", str(BASE_DIR / "tools" / "slack.py"),
             "send", "--workspace", "nalu",
             "--channel", "C08P14TTBA7",  # #nalu-hub
             "--message", message],
            capture_output=True, text=True, cwd=str(BASE_DIR),
        )
        if result.returncode != 0:
            print(f"Slack warning: {result.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"Slack notification failed (non-fatal): {e}", file=sys.stderr)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Cashflow operational expenses sync")
    parser.add_argument("--month", default=datetime.now().strftime("%Y-%m"),
                        help="Month to sync (YYYY-MM, default: current)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would change without writing")
    args = parser.parse_args()
    run_sync(args.month, args.dry_run)


if __name__ == "__main__":
    main()
