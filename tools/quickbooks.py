#!/usr/bin/env python3
"""QuickBooks Online integration tool.

Usage:
  python quickbooks.py auth                  # Run OAuth flow (first time)
  python quickbooks.py refresh               # Refresh access token
  python quickbooks.py company-info          # Test connection
  python quickbooks.py create-expense        # Create an expense
    --vendor "Vendor Name"
    --amount 100.00
    --account "Office Expenses"
    --description "Description"
    [--date 2026-03-06]
  python quickbooks.py list-accounts         # List chart of accounts
  python quickbooks.py list-vendors          # List vendors
  python quickbooks.py list-expenses [--limit 10]  # List recent expenses
"""

import argparse
import json
import os
import sys
import webbrowser
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, "..", "config")
KEYS_FILE = os.path.join(CONFIG_DIR, "api-keys.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "quickbooks-token.json")

QBO_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
QBO_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
QBO_SANDBOX_BASE = "https://sandbox-quickbooks.api.intuit.com/v3/company"
QBO_PROD_BASE = "https://quickbooks.api.intuit.com/v3/company"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "com.intuit.quickbooks.accounting"


def load_keys():
    with open(KEYS_FILE) as f:
        return json.load(f)


def load_token():
    if not os.path.exists(TOKEN_FILE):
        print("No token found. Run: python quickbooks.py auth")
        sys.exit(1)
    with open(TOKEN_FILE) as f:
        return json.load(f)


def save_token(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)


def get_base_url(token_data):
    env = token_data.get("environment", "sandbox")
    if env == "production":
        return QBO_PROD_BASE
    return QBO_SANDBOX_BASE


def api_request(method, endpoint, token_data=None, json_body=None, params=None):
    if token_data is None:
        token_data = load_token()
    base = get_base_url(token_data)
    realm_id = token_data["realm_id"]
    url = f"{base}/{realm_id}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    resp = requests.request(method, url, headers=headers, json=json_body, params=params)
    if resp.status_code == 401:
        print("Token expired. Refreshing...")
        token_data = do_refresh(token_data)
        headers["Authorization"] = f"Bearer {token_data['access_token']}"
        resp = requests.request(method, url, headers=headers, json=json_body, params=params)
    resp.raise_for_status()
    return resp.json()


# --- OAuth Flow ---

def do_auth():
    keys = load_keys()
    client_id = keys["quickbooks_client_id"]
    client_secret = keys["quickbooks_client_secret"]

    auth_params = urlencode({
        "client_id": client_id,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": "jasper-os",
    })
    auth_url = f"{QBO_AUTH_URL}?{auth_params}"

    captured = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            captured["code"] = query.get("code", [None])[0]
            captured["realm_id"] = query.get("realmId", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Connected! You can close this tab.</h2>")

        def log_message(self, format, *args):
            pass

    print(f"Opening browser for QuickBooks authorization...")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8080), CallbackHandler)
    print("Waiting for callback on http://localhost:8080/callback ...")
    server.handle_request()

    code = captured.get("code")
    realm_id = captured.get("realm_id")
    if not code or not realm_id:
        print("ERROR: Did not receive authorization code or realm ID.")
        sys.exit(1)

    print(f"Got auth code. Exchanging for tokens (realm: {realm_id})...")

    resp = requests.post(QBO_TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }, auth=(client_id, client_secret), headers={"Accept": "application/json"})
    resp.raise_for_status()
    token_data = resp.json()
    token_data["realm_id"] = realm_id
    token_data["environment"] = "sandbox"  # Change to "production" when ready

    save_token(token_data)
    print(f"Token saved to {TOKEN_FILE}")
    print("Connection successful! Test with: python quickbooks.py company-info")


def do_refresh(token_data=None):
    if token_data is None:
        token_data = load_token()
    keys = load_keys()

    resp = requests.post(QBO_TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"],
    }, auth=(keys["quickbooks_client_id"], keys["quickbooks_client_secret"]),
       headers={"Accept": "application/json"})
    resp.raise_for_status()
    new_token = resp.json()
    new_token["realm_id"] = token_data["realm_id"]
    new_token["environment"] = token_data.get("environment", "sandbox")
    save_token(new_token)
    print("Token refreshed.")
    return new_token


# --- Commands ---

def cmd_company_info(_args):
    data = api_request("GET", "companyinfo/{0}".format(load_token()["realm_id"]))
    info = data["CompanyInfo"]
    print(f"Company: {info['CompanyName']}")
    print(f"Country: {info.get('Country', 'N/A')}")
    print(f"Email: {info.get('Email', {}).get('Address', 'N/A')}")


def cmd_list_accounts(_args):
    query = "SELECT * FROM Account MAXRESULTS 100"
    data = api_request("GET", "query", params={"query": query})
    accounts = data.get("QueryResponse", {}).get("Account", [])
    if not accounts:
        print("No accounts found.")
        return
    for a in accounts:
        print(f"  [{a['AccountType']}] {a['Name']} (ID: {a['Id']})")


def cmd_list_vendors(_args):
    query = "SELECT * FROM Vendor MAXRESULTS 100"
    data = api_request("GET", "query", params={"query": query})
    vendors = data.get("QueryResponse", {}).get("Vendor", [])
    if not vendors:
        print("No vendors found.")
        return
    for v in vendors:
        print(f"  {v['DisplayName']} (ID: {v['Id']})")


def cmd_list_expenses(args):
    limit = args.limit or 10
    query = f"SELECT * FROM Purchase MAXRESULTS {limit} ORDERBY MetaData.CreateTime DESC"
    data = api_request("GET", "query", params={"query": query})
    purchases = data.get("QueryResponse", {}).get("Purchase", [])
    if not purchases:
        print("No expenses found.")
        return
    for p in purchases:
        total = p.get("TotalAmt", 0)
        txn_date = p.get("TxnDate", "N/A")
        vendor = p.get("EntityRef", {}).get("name", "Unknown")
        print(f"  {txn_date} | {vendor} | ${total:.2f}")


def cmd_create_expense(args):
    token_data = load_token()

    # Look up or create vendor reference
    vendor_ref = None
    if args.vendor:
        query = f"SELECT * FROM Vendor WHERE DisplayName = '{args.vendor}'"
        data = api_request("GET", "query", params={"query": query}, token_data=token_data)
        vendors = data.get("QueryResponse", {}).get("Vendor", [])
        if vendors:
            vendor_ref = {"value": vendors[0]["Id"], "name": vendors[0]["DisplayName"]}
        else:
            print(f"Vendor '{args.vendor}' not found. Creating...")
            new_vendor = api_request("POST", "vendor", json_body={
                "DisplayName": args.vendor
            }, token_data=token_data)
            v = new_vendor["Vendor"]
            vendor_ref = {"value": v["Id"], "name": v["DisplayName"]}

    # Look up account reference
    account_ref = None
    if args.account:
        query = f"SELECT * FROM Account WHERE Name = '{args.account}'"
        data = api_request("GET", "query", params={"query": query}, token_data=token_data)
        accounts = data.get("QueryResponse", {}).get("Account", [])
        if accounts:
            account_ref = {"value": accounts[0]["Id"], "name": accounts[0]["Name"]}
        else:
            print(f"Account '{args.account}' not found. Use 'list-accounts' to see available accounts.")
            sys.exit(1)

    expense_body = {
        "PaymentType": "Cash",
        "TxnDate": args.date or date.today().isoformat(),
        "Line": [{
            "DetailType": "AccountBasedExpenseLineDetail",
            "Amount": args.amount,
            "AccountBasedExpenseLineDetail": {
                "AccountRef": account_ref,
            },
            "Description": args.description or "",
        }],
    }
    if vendor_ref:
        expense_body["EntityRef"] = vendor_ref

    result = api_request("POST", "purchase", json_body=expense_body, token_data=token_data)
    purchase = result["Purchase"]
    print(f"Expense created: ${purchase['TotalAmt']:.2f} on {purchase['TxnDate']} (ID: {purchase['Id']})")


def main():
    parser = argparse.ArgumentParser(description="QuickBooks Online integration")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("auth", help="Run OAuth flow")
    sub.add_parser("refresh", help="Refresh access token")
    sub.add_parser("company-info", help="Show company info")
    sub.add_parser("list-accounts", help="List chart of accounts")
    sub.add_parser("list-vendors", help="List vendors")

    p_expenses = sub.add_parser("list-expenses", help="List recent expenses")
    p_expenses.add_argument("--limit", type=int, default=10)

    p_create = sub.add_parser("create-expense", help="Create an expense")
    p_create.add_argument("--vendor", required=True)
    p_create.add_argument("--amount", type=float, required=True)
    p_create.add_argument("--account", required=True)
    p_create.add_argument("--description", default="")
    p_create.add_argument("--date", default=None)

    args = parser.parse_args()

    if args.command == "auth":
        do_auth()
    elif args.command == "refresh":
        do_refresh()
    elif args.command == "company-info":
        cmd_company_info(args)
    elif args.command == "list-accounts":
        cmd_list_accounts(args)
    elif args.command == "list-vendors":
        cmd_list_vendors(args)
    elif args.command == "list-expenses":
        cmd_list_expenses(args)
    elif args.command == "create-expense":
        cmd_create_expense(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
