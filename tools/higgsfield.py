#!/usr/bin/env python3
"""
Kie.ai image generation tools (Nano Banana Pro).

Usage:
    python3 tools/higgsfield.py generate --prompt "A blue square with white text 'Hello'" --width 1080 --height 1080
    python3 tools/higgsfield.py poll --id "task_nano-banana-pro_123456"
    python3 tools/higgsfield.py generate-and-wait --prompt "..." --aspect-ratio "1:1" --resolution "2K" --n 2

generate:          Submit a text-to-image generation job.
poll:              Check status of a generation by task ID.
generate-and-wait: Submit and poll until complete (returns image URLs).

Uses Kie.ai API with Nano Banana Pro model.
Reads API key from config/api-keys.json (kie key).
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "api-keys.json"
API_BASE = "https://api.kie.ai/api/v1"
POLL_INTERVAL = 5  # seconds between status checks
MAX_WAIT = 300  # max seconds to wait for generation


def load_api_key():
    with open(CONFIG_PATH) as f:
        keys = json.load(f)
    key = keys.get("kie")
    if not key:
        print("ERROR: No kie key found in config/api-keys.json", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(api_key, method, url, data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
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


def generate(api_key, prompt, aspect_ratio="1:1", resolution="2K", output_format="png", image_inputs=None):
    """Submit a text-to-image generation job via Kie.ai."""
    payload = {
        "model": "nano-banana-pro",
        "input": {
            "prompt": prompt,
            "image_input": image_inputs or [],
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": output_format,
        },
    }
    print(f"Submitting generation (nano-banana-pro, {aspect_ratio}, {resolution})...", file=sys.stderr)
    result = api_request(api_key, "POST", f"{API_BASE}/jobs/createTask", data=payload)
    return result


def poll_task(api_key, task_id):
    """Check status of a generation task."""
    url = f"{API_BASE}/jobs/recordInfo?taskId={task_id}"
    result = api_request(api_key, "GET", url)
    return result


def generate_and_wait(api_key, prompt, aspect_ratio="1:1", resolution="2K", output_format="png", n=1, image_inputs=None):
    """Submit generation(s) and poll until complete. Fires n separate requests for n images."""
    tasks = []
    for i in range(n):
        label = f" ({i+1}/{n})" if n > 1 else ""
        result = generate(api_key, prompt, aspect_ratio, resolution, output_format, image_inputs)
        if "error" in result:
            return result
        task_id = result.get("data", {}).get("taskId")
        if not task_id:
            return {"error": "No taskId in response", "response": result}
        print(f"Task started{label}: {task_id}", file=sys.stderr)
        tasks.append(task_id)

    # Poll all tasks
    results = []
    elapsed = 0
    pending = set(tasks)

    while elapsed < MAX_WAIT and pending:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        for task_id in list(pending):
            status_result = poll_task(api_key, task_id)
            if "error" in status_result:
                print(f"  Warning: poll failed for {task_id}: {status_result['error']}", file=sys.stderr)
                continue

            data = status_result.get("data", {})
            state = data.get("state", "unknown")

            if state == "success":
                result_json = data.get("resultJson", "{}")
                try:
                    parsed = json.loads(result_json)
                except json.JSONDecodeError:
                    parsed = {"raw": result_json}
                urls = parsed.get("resultUrls", [])
                results.append({
                    "task_id": task_id,
                    "state": "success",
                    "image_urls": urls,
                    "cost_time_ms": data.get("costTime"),
                })
                pending.discard(task_id)
                print(f"  Completed: {task_id} ({len(urls)} images)", file=sys.stderr)

            elif state == "fail":
                results.append({
                    "task_id": task_id,
                    "state": "fail",
                    "error": data.get("failMsg", "Unknown error"),
                    "fail_code": data.get("failCode", ""),
                })
                pending.discard(task_id)
                print(f"  Failed: {task_id}: {data.get('failMsg', '')}", file=sys.stderr)

            else:
                print(f"  {task_id}: {state} ({elapsed}s elapsed)", file=sys.stderr)

    # Handle timeouts
    for task_id in pending:
        results.append({
            "task_id": task_id,
            "state": "timeout",
            "error": f"Timed out after {MAX_WAIT}s",
        })

    # Flatten all image URLs
    all_urls = []
    for r in results:
        all_urls.extend(r.get("image_urls", []))

    return {
        "total_tasks": len(tasks),
        "completed": sum(1 for r in results if r["state"] == "success"),
        "failed": sum(1 for r in results if r["state"] in ("fail", "timeout")),
        "image_urls": all_urls,
        "tasks": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Kie.ai image generation tools (Nano Banana Pro)")
    subparsers = parser.add_subparsers(dest="command")

    # generate
    gen_cmd = subparsers.add_parser("generate", help="Submit a text-to-image job")
    gen_cmd.add_argument("--prompt", required=True, help="Image generation prompt")
    gen_cmd.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (default: 1:1)")
    gen_cmd.add_argument("--resolution", default="2K", help="Resolution: 1K, 2K, 4K (default: 2K)")
    gen_cmd.add_argument("--format", default="png", dest="output_format", help="Output format (default: png)")

    # poll
    poll_cmd = subparsers.add_parser("poll", help="Check task status")
    poll_cmd.add_argument("--id", required=True, help="Task ID to check")

    # generate-and-wait
    gw_cmd = subparsers.add_parser("generate-and-wait", help="Submit and wait for results")
    gw_cmd.add_argument("--prompt", required=True, help="Image generation prompt")
    gw_cmd.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (default: 1:1)")
    gw_cmd.add_argument("--resolution", default="2K", help="Resolution: 1K, 2K, 4K (default: 2K)")
    gw_cmd.add_argument("--format", default="png", dest="output_format", help="Output format (default: png)")
    gw_cmd.add_argument("--n", type=int, default=1, help="Number of images (fires n separate tasks, default: 1)")

    args = parser.parse_args()
    api_key = load_api_key()

    if args.command == "generate":
        result = generate(api_key, args.prompt, args.aspect_ratio, args.resolution, args.output_format)
        print(json.dumps(result, indent=2))

    elif args.command == "poll":
        result = poll_task(api_key, args.id)
        print(json.dumps(result, indent=2))

    elif args.command == "generate-and-wait":
        result = generate_and_wait(api_key, args.prompt, args.aspect_ratio, args.resolution, args.output_format, args.n)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
