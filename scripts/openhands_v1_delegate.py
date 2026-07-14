#!/usr/bin/env python3
"""Create and monitor delegated OpenHands V1 app conversations.

This helper is dependency-free so a Replicated OpenHands automation can run it
inside a freshly cloned repository.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://app.replicated.rajistics.com"
TERMINAL_EXECUTION_STATUSES = {"finished", "error", "stuck", "stopped", "waiting_for_confirmation"}
TERMINAL_SANDBOX_STATUSES = {"ERROR", "MISSING"}


class OpenHandsV1Error(RuntimeError):
    """Raised when the OpenHands V1 API cannot satisfy a request."""


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum():
            continue
        os.environ.setdefault(key, value.strip().strip("'").strip('"'))


def base_url(explicit_base: str | None = None) -> str:
    return (
        explicit_base
        or os.getenv("OPENHANDS_BASE_URL")
        or os.getenv("OPENHANDS_HOST_RAJISTICS")
        or os.getenv("OPENHANDS_HOST")
        or DEFAULT_BASE_URL
    ).rstrip("/")


def read_api_key() -> str:
    for env_name in (
        "OPENHANDS_API_KEY_RAJISTICS",
        "OPENHANDS_API_KEY",
        "OPENHANDS_API_KEY_ORG",
        "OH_API_KEY",
    ):
        value = os.getenv(env_name)
        if value:
            return value.strip()
    raise OpenHandsV1Error(
        "Missing OpenHands API key. Set one of: OPENHANDS_API_KEY_RAJISTICS, "
        "OPENHANDS_API_KEY, OPENHANDS_API_KEY_ORG, or OH_API_KEY."
    )


def build_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "X-Access-Token": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def endpoint(base: str, path: str, query: dict[str, Any] | None = None) -> str:
    url = base.rstrip("/") + path
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    return url


def request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise OpenHandsV1Error(f"{method} {url} -> HTTP {exc.code}: {raw[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise OpenHandsV1Error(f"{method} {url} failed: {exc}") from exc


def render_prompt(path: Path, variables: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def parse_vars(raw_vars: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in raw_vars:
        if "=" not in item:
            raise OpenHandsV1Error(f"--var must be KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        if not key:
            raise OpenHandsV1Error("--var keys cannot be empty")
        values[key] = value
    return values


def secret_env_map(env_names: list[str]) -> dict[str, str]:
    secrets: dict[str, str] = {}
    for name in env_names:
        value = os.getenv(name)
        if not value:
            raise OpenHandsV1Error(f"Requested child secret env var {name!r} is not set")
        secrets[name] = value
    return secrets


def redact_for_output(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_lower = key.lower()
            if (
                key_lower in {"secrets", "api_key", "session_api_key", "token", "authorization", "value"}
                or "secret" in key_lower
                or "token" in key_lower
                or "password" in key_lower
            ):
                redacted[key] = "<redacted>"
            else:
                redacted[key] = redact_for_output(item)
        return redacted
    if isinstance(value, list):
        return [redact_for_output(item) for item in value]
    return value


def start_app_conversation(
    *,
    base: str,
    headers: dict[str, str],
    prompt: str,
    title: str,
    repository: str | None,
    branch: str | None,
    run: bool = True,
    llm_model: str | None = None,
    parent_conversation_id: str | None = None,
    secrets: dict[str, str] | None = None,
    system_message_suffix: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": title,
        "trigger": "openhands_api",
        "agent_type": "default",
        "public": False,
        "initial_message": {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
            "run": run,
        },
    }
    if repository:
        payload["selected_repository"] = repository
        payload["git_provider"] = "github"
    if branch:
        payload["selected_branch"] = branch
    if llm_model:
        payload["llm_model"] = llm_model
    if parent_conversation_id:
        payload["parent_conversation_id"] = parent_conversation_id
    if secrets:
        payload["secrets"] = secrets
    if system_message_suffix:
        payload["system_message_suffix"] = system_message_suffix
    return request_json("POST", endpoint(base, "/api/v1/app-conversations"), headers, payload, timeout=120)


def app_conversation_record(
    *,
    base: str,
    headers: dict[str, str],
    conversation_id: str,
) -> dict[str, Any]:
    conversations = request_json(
        "GET",
        endpoint(base, "/api/v1/app-conversations", {"ids": conversation_id}),
        headers,
        timeout=60,
    )
    return conversations[0] if isinstance(conversations, list) and conversations else {}


def wait_app_conversation_runtime(
    *,
    base: str,
    headers: dict[str, str],
    conversation_id: str,
    timeout_seconds: int = 120,
    poll_seconds: int = 2,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_record: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last_record = app_conversation_record(base=base, headers=headers, conversation_id=conversation_id)
        if last_record.get("conversation_url") and last_record.get("session_api_key"):
            return last_record
        time.sleep(poll_seconds)
    raise OpenHandsV1Error(
        f"Timed out waiting for runtime URL and session key for child conversation {conversation_id}"
    )


def runtime_endpoint(record: dict[str, Any], path: str) -> str:
    conversation_url = str(record.get("conversation_url") or "")
    parsed = urllib.parse.urlparse(conversation_url)
    if not parsed.scheme or not parsed.netloc:
        raise OpenHandsV1Error("Child conversation record did not include a valid runtime URL")
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def runtime_request_json(
    method: str,
    url: str,
    session_key: str,
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    if not session_key:
        raise OpenHandsV1Error("Child conversation record did not include a session API key")
    headers = {
        "X-Session-API-Key": session_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if not raw:
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise OpenHandsV1Error(f"{method} {url} -> HTTP {exc.code}: {raw[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise OpenHandsV1Error(f"{method} {url} failed: {exc}") from exc


def provision_runtime_secrets(
    *,
    base: str,
    headers: dict[str, str],
    conversation_id: str,
    secrets: dict[str, str],
) -> dict[str, Any]:
    record = wait_app_conversation_runtime(base=base, headers=headers, conversation_id=conversation_id)
    payload = {
        "secrets": {
            name: {"kind": "StaticSecret", "value": value}
            for name, value in secrets.items()
            if value
        }
    }
    if not payload["secrets"]:
        raise OpenHandsV1Error("No non-empty secrets were provided for child conversation provisioning")
    result = runtime_request_json(
        "POST",
        runtime_endpoint(record, f"/api/conversations/{urllib.parse.quote(conversation_id, safe='')}/secrets"),
        str(record.get("session_api_key") or ""),
        payload,
        timeout=60,
    )
    return {"secret_names": sorted(payload["secrets"]), "result": redact_for_output(result)}


def run_runtime_conversation(
    *,
    base: str,
    headers: dict[str, str],
    conversation_id: str,
) -> dict[str, Any]:
    record = wait_app_conversation_runtime(base=base, headers=headers, conversation_id=conversation_id)
    try:
        result = runtime_request_json(
            "POST",
            runtime_endpoint(record, f"/api/conversations/{urllib.parse.quote(conversation_id, safe='')}/run"),
            str(record.get("session_api_key") or ""),
            {},
            timeout=60,
        )
    except OpenHandsV1Error as exc:
        if "HTTP 409" not in str(exc) or "already running" not in str(exc).lower():
            raise
        result = {"status": "already_running"}
    return {"result": redact_for_output(result)}


def poll_start_task(
    *,
    base: str,
    headers: dict[str, str],
    task_id: str,
    timeout_seconds: int = 600,
    poll_seconds: int = 10,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        tasks = request_json(
            "GET",
            endpoint(base, "/api/v1/app-conversations/start-tasks", {"ids": task_id}),
            headers,
            timeout=60,
        )
        task = tasks[0] if isinstance(tasks, list) and tasks else {}
        status = str(task.get("status", "")).upper()
        if task.get("app_conversation_id") or status in {"READY", "ERROR", "FAILED", "STOPPED"}:
            return task
        time.sleep(poll_seconds)
    raise TimeoutError(f"Timed out waiting for OpenHands start task {task_id}")


def poll_conversation(
    *,
    base: str,
    headers: dict[str, str],
    conversation_id: str,
    timeout_seconds: int = 1800,
    poll_seconds: int = 20,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        conversations = request_json(
            "GET",
            endpoint(base, "/api/v1/app-conversations", {"ids": conversation_id}),
            headers,
            timeout=60,
        )
        conversation = conversations[0] if isinstance(conversations, list) and conversations else {}
        execution_status = str(conversation.get("execution_status", "")).lower()
        sandbox_status = str(conversation.get("sandbox_status", ""))
        if execution_status in TERMINAL_EXECUTION_STATUSES or sandbox_status in TERMINAL_SANDBOX_STATUSES:
            return conversation
        time.sleep(poll_seconds)
    raise TimeoutError(f"Timed out waiting for OpenHands conversation {conversation_id}")


def fetch_events(
    *,
    base: str,
    headers: dict[str, str],
    conversation_id: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page_id: str | None = None
    while True:
        query: dict[str, Any] = {"sort_order": "TIMESTAMP", "limit": limit}
        if page_id:
            query["page_id"] = page_id
        page = request_json(
            "GET",
            endpoint(base, f"/api/v1/conversation/{conversation_id}/events/search", query),
            headers,
            timeout=60,
        )
        if not isinstance(page, dict):
            return items
        items.extend(page.get("items", []))
        page_id = page.get("next_page_id")
        if not page_id:
            return items


def content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    chunks: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("type", "text") == "text":
            chunks.append(str(item.get("text", "")))
    return "\n".join(chunk for chunk in chunks if chunk)


def latest_agent_text(events: list[dict[str, Any]]) -> str:
    for event in reversed(events):
        action = event.get("action") if isinstance(event.get("action"), dict) else {}
        if action.get("kind") == "FinishAction" and action.get("message"):
            return str(action.get("message", "")).strip()
    for event in reversed(events):
        if event.get("source") != "agent":
            continue
        llm_message = event.get("llm_message") if isinstance(event.get("llm_message"), dict) else {}
        text = content_text(llm_message.get("content"))
        if text:
            return text.strip()
    return ""


def conversation_summary(base: str, conversation_id: str, record: dict[str, Any] | None = None) -> dict[str, Any]:
    record = record or {}
    return {
        "id": conversation_id,
        "ui_url": f"{base.rstrip('/')}/conversations/{conversation_id}",
        "api_url": f"{base.rstrip('/')}/api/v1/app-conversations?ids={urllib.parse.quote(conversation_id)}",
        "title": record.get("title"),
        "execution_status": record.get("execution_status"),
        "sandbox_status": record.get("sandbox_status"),
        "selected_repository": record.get("selected_repository"),
        "selected_branch": record.get("selected_branch"),
        "conversation_url": record.get("conversation_url"),
    }


def command_start(args: argparse.Namespace) -> int:
    if args.env_file:
        load_env_file(args.env_file)
    base = base_url(args.base_url)
    headers = build_headers(read_api_key())
    prompt = render_prompt(args.prompt_file, parse_vars(args.var))
    start_task = start_app_conversation(
        base=base,
        headers=headers,
        prompt=prompt,
        title=args.title or args.name or "Delegated OpenHands conversation",
        repository=args.repository,
        branch=args.branch,
        run=not args.no_run,
        llm_model=args.llm_model,
        parent_conversation_id=args.parent_conversation_id,
        secrets=secret_env_map(args.secret_env),
    )
    task_id = start_task.get("id")
    summary: dict[str, Any] = {"start_task_id": task_id, "start_task": redact_for_output(start_task)}
    if task_id and not args.no_wait_start:
        task = poll_start_task(
            base=base,
            headers=headers,
            task_id=task_id,
            timeout_seconds=args.start_timeout_seconds,
            poll_seconds=args.poll_seconds,
        )
        conversation_id = task.get("app_conversation_id")
        summary["start_task"] = redact_for_output(task)
        if conversation_id:
            summary.update(conversation_summary(base, conversation_id))
    if args.name:
        summary["name"] = args.name
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def command_wait(args: argparse.Namespace) -> int:
    if args.env_file:
        load_env_file(args.env_file)
    base = base_url(args.base_url)
    headers = build_headers(read_api_key())
    record = poll_conversation(
        base=base,
        headers=headers,
        conversation_id=args.conversation_id,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    events = fetch_events(base=base, headers=headers, conversation_id=args.conversation_id)
    summary = conversation_summary(base, args.conversation_id, record)
    summary["final_text"] = latest_agent_text(events)
    print(json.dumps(summary, indent=2, sort_keys=True))
    status = str(record.get("execution_status", "")).lower()
    return 0 if status in {"finished", "idle"} else 1


def command_render(args: argparse.Namespace) -> int:
    print(render_prompt(args.prompt_file, parse_vars(args.var)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="OpenHands base URL")
    parser.add_argument("--env-file", type=Path, help="optional KEY=value env file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--name")
    start.add_argument("--title")
    start.add_argument("--prompt-file", type=Path, required=True)
    start.add_argument("--repository", help="selected repository, for example owner/repo")
    start.add_argument("--branch", help="selected branch")
    start.add_argument("--llm-model", help="optional model override")
    start.add_argument("--parent-conversation-id", help="optional parent app conversation id")
    start.add_argument(
        "--secret-env",
        action="append",
        default=[],
        help="pass this environment variable as a child secret by the same name",
    )
    start.add_argument("--var", action="append", default=[], help="template substitution KEY=VALUE")
    start.add_argument("--no-run", action="store_true")
    start.add_argument("--no-wait-start", action="store_true")
    start.add_argument("--start-timeout-seconds", type=int, default=600)
    start.add_argument("--poll-seconds", type=int, default=10)
    start.set_defaults(func=command_start)

    wait = subparsers.add_parser("wait")
    wait.add_argument("conversation_id")
    wait.add_argument("--timeout-seconds", type=int, default=1800)
    wait.add_argument("--poll-seconds", type=int, default=20)
    wait.set_defaults(func=command_wait)

    render = subparsers.add_parser("render")
    render.add_argument("--prompt-file", type=Path, required=True)
    render.add_argument("--var", action="append", default=[])
    render.set_defaults(func=command_render)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OpenHandsV1Error, TimeoutError) as exc:
        print(f"openhands_v1_delegate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
