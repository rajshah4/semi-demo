#!/usr/bin/env python3
"""Dry-run or register GitHub prompt-preset automations for the semi demo."""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PACKAGES = [
    {
        "slug": "openhands-foundry-parent",
        "name": "Semi Demo Foundry Parent",
        "path": "automations/github/openhands-foundry-parent/prompt.md",
        "event": "issues.labeled",
        "filter": "label.name == 'openhands-foundry-parent'",
    },
    {
        "slug": "openhands-rtl-context",
        "name": "Semi Demo RTL Context Scout",
        "path": "automations/github/openhands-rtl-context/prompt.md",
        "event": "issues.labeled",
        "filter": "label.name == 'openhands-rtl-context'",
    },
    {
        "slug": "openhands-rtl-build",
        "name": "Semi Demo RTL Build",
        "path": "automations/github/openhands-rtl-build/prompt.md",
        "event": "issues.labeled",
        "filter": "label.name == 'openhands-rtl-build'",
    },
    {
        "slug": "openhands-rtl-sidekick",
        "name": "Semi Demo RTL Sidekick",
        "path": "automations/github/openhands-rtl-sidekick/prompt.md",
        "event": "issues.labeled",
        "filter": "label.name == 'openhands-rtl-sidekick'",
    },
    {
        "slug": "openhands-rtl-qa",
        "name": "Semi Demo RTL QA",
        "path": "automations/github/openhands-rtl-qa/prompt.md",
        "event": "pull_request.labeled",
        "filter": "label.name == 'openhands-rtl-qa'",
    },
    {
        "slug": "openhands-rtl-review",
        "name": "Semi Demo RTL Review",
        "path": "automations/github/openhands-rtl-review/prompt.md",
        "event": "pull_request.labeled",
        "filter": "label.name == 'openhands-rtl-review'",
    },
    {
        "slug": "openhands-rtl-model-switch",
        "name": "Semi Demo RTL Model Switch Proof",
        "path": "automations/github/openhands-rtl-model-switch/prompt.md",
        "event": "issues.labeled",
        "filter": "label.name == 'openhands-rtl-model-switch'",
    },
]


def build_payload(package: dict[str, str]) -> dict:
    prompt = (ROOT / package["path"]).read_text()
    payload = {
        "name": package["name"],
        "prompt": prompt,
        "trigger": {
            "type": "event",
            "source": "github",
            "on": package["event"],
            "filter": package["filter"],
        },
        "timeout": 900,
    }

    repo_url = os.environ.get("GITHUB_DEMO_REPO_URL")
    repo_name = os.environ.get("GITHUB_DEMO_REPOSITORY")
    if repo_url:
        payload["repos"] = [repo_url]
    elif repo_name:
        payload["repos"] = [{"url": repo_name, "provider": "github"}]

    return payload


def post_payload(host: str, api_key: str, payload: dict) -> dict:
    url = host.rstrip("/") + "/api/automation/v1/preset/prompt"
    body = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="register automations")
    parser.add_argument("--dry-run", action="store_true", help="print payloads only")
    parser.add_argument(
        "--only",
        action="append",
        choices=[package["slug"] for package in PACKAGES],
        help="register or print one package; may be provided more than once",
    )
    args = parser.parse_args()

    apply = args.apply and not args.dry_run
    packages = [package for package in PACKAGES if not args.only or package["slug"] in args.only]
    payloads = [build_payload(package) for package in packages]

    if not apply:
        print(json.dumps(payloads, indent=2))
        return

    host = os.environ.get("OPENHANDS_HOST_GITHUB") or os.environ.get("OPENHANDS_HOST")
    api_key = os.environ.get("OPENHANDS_API_KEY_GITHUB") or os.environ.get("OPENHANDS_API_KEY")
    if not host or not api_key:
        raise SystemExit("OPENHANDS_HOST_GITHUB and OPENHANDS_API_KEY_GITHUB are required for --apply")

    for payload in payloads:
        result = post_payload(host, api_key, payload)
        print(json.dumps({"name": payload["name"], "result": result}, indent=2))


if __name__ == "__main__":
    main()
