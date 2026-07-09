#!/usr/bin/env python3
"""Deterministic preflight checks for the semiconductor demo scaffold."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "configs/model-routing.yaml",
    "configs/meta-profile.semi-foundry-router.example.json",
    "workflows/foundry-rtl-workflow.yaml",
    "workflows/foundry-rtl-sidekick-workflow.yaml",
    "events/new-rtl-block.json",
    "automation/foundry-rtl-request.prompt.md",
    "automation/preset-payload.example.json",
    "docs/demo-script.md",
    "docs/live-demo-script.md",
    "docs/work-cells.md",
    "docs/parent-child-conversations.md",
    "docs/intelligent-model-routing.md",
    "docs/repo-memory/model-routing-policy.md",
    ".github/labels.json",
    ".github/ISSUE_TEMPLATE/rtl_request.md",
    "automations/github/openhands-rtl-context/prompt.md",
    "automations/github/openhands-rtl-build/prompt.md",
    "automations/github/openhands-rtl-sidekick/prompt.md",
    "automations/github/openhands-rtl-qa/prompt.md",
    "automations/github/openhands-rtl-review/prompt.md",
    "skills/foundry-sidekick-launcher/SKILL.md",
    "skills/foundry-context-sidekick/SKILL.md",
]

JSON_FILES = [
    "events/new-rtl-block.json",
    "automation/preset-payload.example.json",
    ".github/labels.json",
    "configs/meta-profile.semi-foundry-router.example.json",
]

FORBIDDEN_MARKERS = [
    "sk-",
    "ghp_",
    "hf_",
    "OPENHANDS_API_KEY=",
    "SAMBANOVA_API_KEY=",
    "HF_TOKEN=",
]


def fail(message: str) -> None:
    raise SystemExit(f"preflight failed: {message}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    for path in JSON_FILES:
        try:
            json.loads((ROOT / path).read_text())
        except json.JSONDecodeError as exc:
            fail(f"{path} is not valid JSON: {exc}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix in {".png", ".gif", ".jpg", ".jpeg", ".pdf"}:
            continue
        text = path.read_text(errors="ignore")
        for marker in FORBIDDEN_MARKERS:
            if marker in text and path.name != "preflight_semi_demo.py":
                fail(f"possible secret marker {marker!r} in {path.relative_to(ROOT)}")

    print("preflight passed")
    print(f"checked {len(REQUIRED_FILES)} required files")
    print(f"validated {len(JSON_FILES)} JSON files")


if __name__ == "__main__":
    main()
