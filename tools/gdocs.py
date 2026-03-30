#!/usr/bin/env python3
"""
Google Docs tool for duplicating, creating, and updating documents.

Usage:
    python3 tools/gdocs.py --account nalu duplicate --template-id "DOC_ID" --title "New Doc Title"
    python3 tools/gdocs.py --account nalu get --doc-id "DOC_ID"
    python3 tools/gdocs.py --account nalu replace --doc-id "DOC_ID" --placeholder "{{KEY}}" --value "replacement text"
    python3 tools/gdocs.py --account nalu batch-replace --doc-id "DOC_ID" --replacements '{"{{KEY1}}":"val1","{{KEY2}}":"val2"}'
    python3 tools/gdocs.py --account nalu share --doc-id "DOC_ID" --email "user@example.com" --role "reader"
    python3 tools/gdocs.py --account nalu list-folder --folder-id "FOLDER_ID"
    python3 tools/gdocs.py --account nalu search-folder --parent-id "PARENT_ID" --name "folder name"
    python3 tools/gdocs.py --account nalu create-doc --title "Doc Title" --folder-id "FOLDER_ID"

Accounts: cn (hello@clientnetwork.io, default), nalu (hello@nalupodcasts.com).
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"

ACCOUNTS = {
    "cn": {"token": "google-token.json"},
    "nalu": {"token": "google-token-nalu.json"},
}

_active_token_path = CONFIG_DIR / "google-token.json"


def set_account(name):
    global _active_token_path
    account = ACCOUNTS.get(name)
    if not account:
        print(f"ERROR: Unknown account '{name}'. Available: {', '.join(ACCOUNTS.keys())}", file=sys.stderr)
        sys.exit(1)
    _active_token_path = CONFIG_DIR / account["token"]


def load_token():
    with open(_active_token_path) as f:
        return json.load(f)


def save_token(token_data):
    with open(_active_token_path, "w") as f:
        json.dump(token_data, f, indent=2)


def refresh_access_token(token_data):
    data = {
        "client_id": token_data["client_id"],
        "client_secret": token_data["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token"
    }
    body = "&".join(f"{k}={v}" for k, v in data.items()).encode()
    req = urllib.request.Request(
        token_data["token_uri"],
        data=body,
        method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())

    token_data["token"] = result["access_token"]
    save_token(token_data)
    return token_data["token"]


def api_request(access_token, method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": error_body}


def api_request_with_refresh(method, url, data=None):
    token_data = load_token()
    access_token = token_data["token"]

    result = api_request(access_token, method, url, data)

    if isinstance(result, dict) and "error" in result and "401" in str(result.get("error", "")):
        print("Access token expired, refreshing...", file=sys.stderr)
        access_token = refresh_access_token(token_data)
        result = api_request(access_token, method, url, data)

    return result


def duplicate_doc(template_id, title, folder_id=None):
    """Duplicate a Google Doc using the Drive API copy endpoint."""
    url = f"https://www.googleapis.com/drive/v3/files/{template_id}/copy"
    body = {"name": title}
    if folder_id:
        body["parents"] = [folder_id]

    result = api_request_with_refresh("POST", url, body)
    return result


def get_doc(doc_id):
    """Get a Google Doc's content via the Docs API."""
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}"
    return api_request_with_refresh("GET", url)


def replace_text(doc_id, placeholder, value):
    """Replace all instances of a placeholder with a value."""
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
    body = {
        "requests": [
            {
                "replaceAllText": {
                    "containsText": {
                        "text": placeholder,
                        "matchCase": True
                    },
                    "replaceText": value
                }
            }
        ]
    }
    return api_request_with_refresh("POST", url, body)


def batch_replace_text(doc_id, replacements):
    """Replace multiple placeholders at once."""
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
    requests = []
    for placeholder, value in replacements.items():
        requests.append({
            "replaceAllText": {
                "containsText": {
                    "text": placeholder,
                    "matchCase": True
                },
                "replaceText": value
            }
        })

    body = {"requests": requests}
    return api_request_with_refresh("POST", url, body)


def write_at(doc_id, operations):
    """Write text at specific indices. Each operation: {start, end, text}.
    Deletes content in [start, end) then inserts text at start.
    Operations are processed bottom-to-top to preserve indices."""
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
    # Sort operations by start index descending to avoid index shifts
    sorted_ops = sorted(operations, key=lambda o: o["start"], reverse=True)
    requests = []
    for op in sorted_ops:
        # Delete existing content if range is non-empty
        if op["end"] > op["start"]:
            requests.append({
                "deleteContentRange": {
                    "range": {
                        "startIndex": op["start"],
                        "endIndex": op["end"]
                    }
                }
            })
        # Insert new text
        if op.get("text"):
            requests.append({
                "insertText": {
                    "location": {"index": op["start"]},
                    "text": op["text"]
                }
            })
    body = {"requests": requests}
    return api_request_with_refresh("POST", url, body)


def share_doc(doc_id, email, role="reader"):
    """Share a document with a specific email address."""
    url = f"https://www.googleapis.com/drive/v3/files/{doc_id}/permissions"
    body = {
        "type": "user",
        "role": role,
        "emailAddress": email
    }
    # sendNotificationEmail=false to avoid spamming
    url += "?sendNotificationEmail=false"
    return api_request_with_refresh("POST", url, body)


def list_folder(folder_id):
    """List all files and subfolders in a Drive folder."""
    url = (
        f"https://www.googleapis.com/drive/v3/files"
        f"?q='{folder_id}'+in+parents+and+trashed=false"
        f"&fields=files(id,name,mimeType)"
        f"&pageSize=100"
    )
    result = api_request_with_refresh("GET", url)
    if isinstance(result, dict) and "error" in result:
        return result
    files = result.get("files", [])
    return {"files": sorted(files, key=lambda f: f["name"])}


def search_folder(parent_id, name):
    """Search for a folder by name (case-insensitive contains) under a parent."""
    import urllib.parse
    escaped = name.replace("'", "\\'")
    q = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and name contains '{escaped}' and trashed=false"
    url = (
        f"https://www.googleapis.com/drive/v3/files"
        f"?q={urllib.parse.quote(q, safe='')}"
        f"&fields=files(id,name)"
        f"&pageSize=20"
    )
    result = api_request_with_refresh("GET", url)
    if isinstance(result, dict) and "error" in result:
        return result
    return {"files": result.get("files", [])}


def create_doc(title, folder_id=None):
    """Create a new blank Google Doc, optionally in a specific folder."""
    url = "https://www.googleapis.com/drive/v3/files"
    body = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document"
    }
    if folder_id:
        body["parents"] = [folder_id]
    result = api_request_with_refresh("POST", url, body)
    if isinstance(result, dict) and "id" in result:
        result["url"] = f"https://docs.google.com/document/d/{result['id']}/edit"
    return result


def move_doc(doc_id, dest_folder_id):
    """Move a document to a different Drive folder."""
    # First get current parents
    url = f"https://www.googleapis.com/drive/v3/files/{doc_id}?fields=parents"
    result = api_request_with_refresh("GET", url)
    if isinstance(result, dict) and "error" in result:
        return result

    current_parents = ",".join(result.get("parents", []))
    # Move by adding new parent and removing old
    url = f"https://www.googleapis.com/drive/v3/files/{doc_id}?addParents={dest_folder_id}&removeParents={current_parents}"
    return api_request_with_refresh("PATCH", url, {})


def main():
    parser = argparse.ArgumentParser(description="Google Docs tool")
    parser.add_argument("--account", default="cn", choices=list(ACCOUNTS.keys()),
                        help="Google account to use (default: cn)")
    subparsers = parser.add_subparsers(dest="command")

    # duplicate
    dup_cmd = subparsers.add_parser("duplicate", help="Duplicate a template document")
    dup_cmd.add_argument("--template-id", required=True, help="Google Doc ID of the template")
    dup_cmd.add_argument("--title", required=True, help="Title for the new document")
    dup_cmd.add_argument("--folder-id", help="Optional Drive folder ID to place the copy in")

    # get
    get_cmd = subparsers.add_parser("get", help="Get document content")
    get_cmd.add_argument("--doc-id", required=True, help="Google Doc ID")

    # replace
    rep_cmd = subparsers.add_parser("replace", help="Replace placeholder text")
    rep_cmd.add_argument("--doc-id", required=True, help="Google Doc ID")
    rep_cmd.add_argument("--placeholder", required=True, help="Text to find")
    rep_cmd.add_argument("--value", required=True, help="Replacement text")

    # batch-replace
    brep_cmd = subparsers.add_parser("batch-replace", help="Replace multiple placeholders")
    brep_cmd.add_argument("--doc-id", required=True, help="Google Doc ID")
    brep_cmd.add_argument("--replacements", required=True, help="JSON object of placeholder:value pairs")

    # write-at
    wat_cmd = subparsers.add_parser("write-at", help="Write text at specific indices")
    wat_cmd.add_argument("--doc-id", required=True, help="Google Doc ID")
    wat_cmd.add_argument("--operations", required=True,
                         help='JSON array of {start, end, text} objects')

    # share
    share_cmd = subparsers.add_parser("share", help="Share document with a user")
    share_cmd.add_argument("--doc-id", required=True, help="Google Doc ID")
    share_cmd.add_argument("--email", required=True, help="Email to share with")
    share_cmd.add_argument("--role", default="reader", choices=["reader", "writer", "commenter"],
                           help="Permission role (default: reader)")

    # list-folder
    lf_cmd = subparsers.add_parser("list-folder", help="List files and subfolders in a Drive folder")
    lf_cmd.add_argument("--folder-id", required=True, help="Drive folder ID")

    # search-folder
    sf_cmd = subparsers.add_parser("search-folder", help="Search for a subfolder by name")
    sf_cmd.add_argument("--parent-id", required=True, help="Parent folder ID to search within")
    sf_cmd.add_argument("--name", required=True, help="Folder name to search for (case-insensitive contains)")

    # create-doc
    cd_cmd = subparsers.add_parser("create-doc", help="Create a new blank Google Doc")
    cd_cmd.add_argument("--title", required=True, help="Document title")
    cd_cmd.add_argument("--folder-id", help="Optional Drive folder ID to create the doc in")

    # move
    move_cmd = subparsers.add_parser("move", help="Move document to a folder")
    move_cmd.add_argument("--doc-id", required=True, help="Google Doc ID")
    move_cmd.add_argument("--folder-id", required=True, help="Destination folder ID")

    args = parser.parse_args()
    set_account(args.account)

    if args.command == "duplicate":
        result = duplicate_doc(args.template_id, args.title, args.folder_id)
        print(json.dumps(result, indent=2))
    elif args.command == "get":
        result = get_doc(args.doc_id)
        print(json.dumps(result, indent=2))
    elif args.command == "replace":
        result = replace_text(args.doc_id, args.placeholder, args.value)
        print(json.dumps(result, indent=2))
    elif args.command == "batch-replace":
        replacements = json.loads(args.replacements)
        result = batch_replace_text(args.doc_id, replacements)
        print(json.dumps(result, indent=2))
    elif args.command == "write-at":
        operations = json.loads(args.operations)
        result = write_at(args.doc_id, operations)
        print(json.dumps(result, indent=2))
    elif args.command == "share":
        result = share_doc(args.doc_id, args.email, args.role)
        print(json.dumps(result, indent=2))
    elif args.command == "list-folder":
        result = list_folder(args.folder_id)
        print(json.dumps(result, indent=2))
    elif args.command == "search-folder":
        result = search_folder(args.parent_id, args.name)
        print(json.dumps(result, indent=2))
    elif args.command == "create-doc":
        result = create_doc(args.title, args.folder_id)
        print(json.dumps(result, indent=2))
    elif args.command == "move":
        result = move_doc(args.doc_id, args.folder_id)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)

    if isinstance(result, dict) and "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
