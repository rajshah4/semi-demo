#!/usr/bin/env python3
"""Run the Jira-triggered delegated foundry RTL flow on OpenHands v1."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

import openhands_v1_delegate as oh


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT_ROOT = REPO_ROOT / "automations" / "jira" / "rtl-request-parent" / "workcells"
ACTIVE_WORK_CELLS = ("rtl-specialist", "eda-qa")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(oh.redact_for_output(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def adf_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    chunks: list[str] = []
    if isinstance(value, dict):
        if value.get("type") == "text" and value.get("text"):
            chunks.append(str(value["text"]))
        for child in value.get("content", []) or []:
            child_text = adf_text(child)
            if child_text:
                chunks.append(child_text)
    elif isinstance(value, list):
        for child in value:
            child_text = adf_text(child)
            if child_text:
                chunks.append(child_text)
    return "\n".join(chunks)


def jira_headers() -> dict[str, str]:
    token = os.getenv("JIRA_API_TOKEN")
    if not token:
        raise RuntimeError("JIRA_API_TOKEN is required to fetch or comment on Jira issues")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def jira_base_url() -> str:
    base = os.getenv("JIRA_API_BASE_URL")
    if not base:
        raise RuntimeError("JIRA_API_BASE_URL is required to fetch or comment on Jira issues")
    return base.rstrip("/")


def jira_request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        jira_base_url() + path,
        data=data,
        method=method,
        headers=jira_headers(),
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        if not raw:
            return None
        return json.loads(raw)


def fetch_jira_issue(issue_key: str) -> dict[str, str]:
    issue = jira_request(
        "GET",
        f"/rest/api/3/issue/{issue_key}?fields=summary,description,issuetype,project",
    )
    fields = issue.get("fields", {}) if isinstance(issue, dict) else {}
    summary = fields.get("summary") or issue_key
    description = adf_text(fields.get("description")).strip()
    site = os.getenv("JIRA_SITE_URL", "").rstrip("/")
    return {
        "issue_key": issue_key,
        "request_title": summary,
        "request_body": description or summary,
        "issue_url": f"{site}/browse/{issue_key}" if site else "",
    }


def jira_comment_body(text: str) -> dict[str, Any]:
    content = []
    for line in text.splitlines() or [text]:
        content.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": line or " "}],
            }
        )
    return {"body": {"type": "doc", "version": 1, "content": content}}


def post_jira_comment(issue_key: str, text: str) -> None:
    jira_request("POST", f"/rest/api/3/issue/{issue_key}/comment", jira_comment_body(text))


def parse_status(final_text: str, fallback: str) -> str:
    for line in final_text.splitlines():
        if line.lower().startswith("status:"):
            return line.split(":", 1)[1].strip().split()[0].lower()
    return fallback


def default_parent_conversation_id() -> str:
    for env_name in (
        "PARENT_CONVERSATION_ID",
        "APP_CONVERSATION_ID",
        "OPENHANDS_CONVERSATION_ID",
        "OH_CONVERSATION_ID",
        "CONVERSATION_ID",
    ):
        value = os.getenv(env_name)
        if value:
            return value.strip()
    return ""


def find_parent_conversation(base: str, headers: dict[str, str], explicit_id: str = "") -> dict[str, Any]:
    if explicit_id:
        conversations = oh.request_json(
            "GET",
            oh.endpoint(base, "/api/v1/app-conversations", {"ids": explicit_id}),
            headers,
            timeout=60,
        )
        return conversations[0] if isinstance(conversations, list) and conversations else {}

    runtime_id = os.getenv("RUNTIME_ID", "").strip()
    if not runtime_id:
        return {}

    page = oh.request_json(
        "GET",
        oh.endpoint(base, "/api/v1/app-conversations/search", {"limit": 50}),
        headers,
        timeout=60,
    )
    for conversation in page.get("items", []) if isinstance(page, dict) else []:
        if runtime_id and runtime_id in str(conversation.get("conversation_url", "")):
            return conversation
    return {}


def read_scoped_secret(
    *,
    base: str,
    sandbox_id: str,
    session_api_key: str,
    secret_name: str,
) -> str:
    headers = {
        "X-Session-API-Key": session_api_key,
        "Accept": "application/json",
    }
    value = oh.request_json(
        "GET",
        oh.endpoint(base, f"/api/v1/sandboxes/{sandbox_id}/settings/secrets/{secret_name}"),
        headers,
        timeout=60,
    )
    if isinstance(value, str):
        return value
    return str(value or "")


def get_secret_for_child(
    *,
    base: str,
    parent_conversation: dict[str, Any],
    secret_name: str,
) -> str:
    value = os.getenv(secret_name)
    if value:
        return value

    sandbox_id = str(parent_conversation.get("sandbox_id") or "")
    session_key = os.getenv("SESSION_API_KEY", "")
    if sandbox_id and session_key:
        value = read_scoped_secret(
            base=base,
            sandbox_id=sandbox_id,
            session_api_key=session_key,
            secret_name=secret_name,
        )
        if value:
            return value

    raise RuntimeError(f"{secret_name} is required for the RTL specialist child")


def variables_for_cell(args: argparse.Namespace, cell: str, prior_summary: str) -> dict[str, str]:
    return {
        "run_id": args.run_id,
        "repo_slug": args.repo_slug,
        "branch": args.branch,
        "issue_key": args.issue_key,
        "issue_url": args.issue_url or "",
        "request_title": args.request_title,
        "request_body": args.request_body,
        "prior_summary": prior_summary,
        "artifact_path": f"factory_runs/{args.run_id}/{cell}.md",
        "parent_final_artifact": f"factory_runs/{args.run_id}/{cell}.final.md",
    }


def start_and_wait_cell(
    *,
    args: argparse.Namespace,
    base: str,
    headers: dict[str, str],
    run_dir: Path,
    cell: str,
    prior_summary: str,
    parent_conversation_id: str,
    child_secrets: dict[str, str] | None = None,
) -> dict[str, Any]:
    prompt = oh.render_prompt(PROMPT_ROOT / f"{cell}.md", variables_for_cell(args, cell, prior_summary))
    entry: dict[str, Any] = {"name": cell, "start_attempts": []}
    start_task: dict[str, Any] = {}
    conversation_id = ""
    for attempt in range(1, 4):
        start = oh.start_app_conversation(
            base=base,
            headers=headers,
            prompt=prompt,
            title=f"{args.issue_key} foundry {cell}",
            repository=args.repo_slug,
            branch=args.branch,
            llm_model=args.child_llm_model,
            parent_conversation_id=None,
            secrets=child_secrets,
            run=True,
            system_message_suffix=(
                "Foundry demo child conversation. Keep outputs concise, evidence-backed, "
                "and secret-safe. Never print token or environment values."
            ),
        )
        start_task_id = start.get("id")
        attempt_record: dict[str, Any] = {
            "attempt": attempt,
            "start_task_id": start_task_id,
            "start_task": oh.redact_for_output(start),
        }
        entry["start_attempts"].append(attempt_record)
        entry["start_task_id"] = start_task_id
        entry["start_task"] = oh.redact_for_output(start)
        if not start_task_id:
            entry["status"] = "failed"
            entry["error"] = "OpenHands did not return a start task id"
            return entry

        start_task = oh.poll_start_task(
            base=base,
            headers=headers,
            task_id=start_task_id,
            timeout_seconds=args.start_timeout_seconds,
            poll_seconds=args.poll_seconds,
        )
        conversation_id = str(start_task.get("app_conversation_id") or "")
        attempt_record["start_task_result"] = oh.redact_for_output(start_task)
        entry["start_task"] = oh.redact_for_output(start_task)
        if conversation_id:
            break

        detail = str(start_task.get("detail") or start_task.get("error") or "")
        retryable_git_provider_error = (
            "git provider" in detail.lower()
            or "remote url" in detail.lower()
            or "authentication issue" in detail.lower()
        )
        if attempt == 3 or not retryable_git_provider_error:
            entry["status"] = "failed"
            entry["error"] = "OpenHands start task did not return an app conversation id"
            entry["start_task_detail"] = detail
            return entry
        time.sleep(min(30, 5 * attempt))

    entry.update(oh.conversation_summary(base, conversation_id))
    write_json(run_dir / f"{cell}.conversation.json", entry)

    terminal = oh.poll_conversation(
        base=base,
        headers=headers,
        conversation_id=conversation_id,
        timeout_seconds=args.cell_timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    events = oh.fetch_events(base=base, headers=headers, conversation_id=conversation_id)
    final_text = oh.latest_agent_text(events)
    status = parse_status(final_text, str(terminal.get("execution_status", "unknown")).lower())

    entry["wait"] = oh.conversation_summary(base, conversation_id, terminal)
    entry["status"] = status
    entry["final_text"] = final_text
    write_json(run_dir / f"{cell}.wait.json", entry["wait"])
    write_text(run_dir / f"{cell}.final.md", final_text + ("\n" if final_text else ""))
    return entry


def create_manifest(args: argparse.Namespace, run_dir: Path, parent_conversation_id: str) -> None:
    lines = [
        "# Foundry Delegated RTL Run",
        "",
        f"- Run id: `{args.run_id}`",
        f"- Parent conversation: `{parent_conversation_id or 'unknown'}`",
        f"- Jira issue: `{args.issue_key}`",
        f"- Jira URL: {args.issue_url or 'unknown'}",
        f"- Repository: `{args.repo_slug}`",
        f"- Request: {args.request_title}",
        "",
        "## Work Cells",
        "",
        "| Work cell | Status | Conversation |",
        "| --- | --- | --- |",
    ]
    for cell in args.cells:
        lines.append(f"| `{cell}` | pending | - |")
    lines.append("")
    write_text(run_dir / "manifest.md", "\n".join(lines))


def lifecycle_report(args: argparse.Namespace, entries: list[dict[str, Any]], parent_conversation_id: str) -> str:
    lines = [
        "# Foundry Delegated RTL Lifecycle Report",
        "",
        f"- Parent conversation: `{parent_conversation_id or 'unknown'}`",
        f"- Jira issue: `{args.issue_key}`",
        f"- Jira URL: {args.issue_url or 'unknown'}",
        f"- Repository: `{args.repo_slug}`",
        f"- Request: {args.request_title}",
        "",
        "## Child Conversations",
        "",
        "| Work cell | Status | Conversation | Artifact |",
        "| --- | --- | --- | --- |",
    ]
    for entry in entries:
        url = entry.get("ui_url") or ""
        link = f"[{entry.get('id')}]({url})" if entry.get("id") and url else "-"
        artifact = f"`factory_runs/{args.run_id}/{entry['name']}.final.md`"
        lines.append(f"| `{entry['name']}` | {entry.get('status', 'unknown')} | {link} | {artifact} |")
    lines.extend(["", "## Model Routing Evidence", ""])
    lines.append("- Parent selected the RTL specialist lane for RTL/SystemVerilog implementation.")
    lines.append("- The RTL child was created through Conversation v1 with `HF_TOKEN` passed as a child-scoped secret.")
    lines.append("- The QA child uses deterministic EDA/tool evidence as the correctness authority.")
    lines.extend(
        [
            "",
            "## Human Next Step",
            "",
            "Review the child conversation outputs and the generated PR before merge.",
            "",
        ]
    )
    return "\n".join(lines)


def jira_summary_comment(args: argparse.Namespace, entries: list[dict[str, Any]]) -> str:
    child_lines = []
    for entry in entries:
        url = entry.get("ui_url") or "no conversation URL"
        child_lines.append(f"- {entry['name']}: {entry.get('status', 'unknown')} - {url}")
    return "\n".join(
        [
            "OpenHands delegated foundry RTL run complete",
            f"Issue: {args.issue_key}",
            f"Run id: {args.run_id}",
            f"Repository: {args.repo_slug}",
            "Child conversations:",
            *child_lines,
            "Human next step: review the child outputs and generated PR before merge.",
        ]
    )


def run_factory(args: argparse.Namespace) -> int:
    if args.env_file:
        oh.load_env_file(args.env_file)
    if args.issue_key and (not args.request_title or not args.request_body):
        issue = fetch_jira_issue(args.issue_key)
        args.request_title = args.request_title or issue["request_title"]
        args.request_body = args.request_body or issue["request_body"]
        args.issue_url = args.issue_url or issue["issue_url"]

    base = oh.base_url(args.base_url)
    headers = oh.build_headers(oh.read_api_key())
    parent_conversation = find_parent_conversation(
        base,
        headers,
        explicit_id=args.parent_conversation_id or default_parent_conversation_id(),
    )
    parent_conversation_id = str(parent_conversation.get("id") or args.parent_conversation_id or "")
    hf_token = get_secret_for_child(base=base, parent_conversation=parent_conversation, secret_name="HF_TOKEN")

    run_dir = REPO_ROOT / "factory_runs" / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    create_manifest(args, run_dir, parent_conversation_id)

    entries: list[dict[str, Any]] = []
    prior_summary = ""
    for cell in args.cells:
        child_secrets = {"HF_TOKEN": hf_token} if cell == "rtl-specialist" else None
        entry = start_and_wait_cell(
            args=args,
            base=base,
            headers=headers,
            run_dir=run_dir,
            cell=cell,
            prior_summary=prior_summary,
            parent_conversation_id=parent_conversation_id,
            child_secrets=child_secrets,
        )
        entries.append(entry)
        write_json(run_dir / "children.json", entries)
        prior_summary += f"\n\n## {cell}\nstatus: {entry.get('status')}\nurl: {entry.get('ui_url')}\n{entry.get('final_text', '')}"
        if entry.get("status") in {"failed", "needs-human"}:
            break

    report = lifecycle_report(args, entries, parent_conversation_id)
    write_text(run_dir / "lifecycle-report.md", report)
    if args.post_jira_comment and args.issue_key:
        post_jira_comment(args.issue_key, jira_summary_comment(args, entries))
    print(json.dumps({"run_dir": str(run_dir), "entries": oh.redact_for_output(entries)}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="OpenHands base URL")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--repo-slug", required=True)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--run-id", default=time.strftime("foundry-factory-%Y%m%d-%H%M%S"))
    parser.add_argument("--issue-key", required=True)
    parser.add_argument("--issue-url")
    parser.add_argument("--request-title")
    parser.add_argument("--request-body")
    parser.add_argument("--parent-conversation-id")
    parser.add_argument("--cells", nargs="+", choices=ACTIVE_WORK_CELLS, default=list(ACTIVE_WORK_CELLS))
    parser.add_argument("--child-llm-model")
    parser.add_argument("--start-timeout-seconds", type=int, default=600)
    parser.add_argument("--cell-timeout-seconds", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--post-jira-comment", action="store_true")
    return parser


def main() -> int:
    return run_factory(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
