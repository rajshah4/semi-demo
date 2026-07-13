#!/usr/bin/env python3
"""Call ChipCraftX RTLGen through Hugging Face and persist evidence.

This helper is intentionally stdlib-only so it can run inside OpenHands
automation sandboxes without dependency installation. It never prints tokens.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "chipcraftx-io/chipcraftx-rtlgen-7b"
DEFAULT_PROVIDER_SUFFIX = "featherless-ai"
DEFAULT_COMPLETION_ENDPOINT = "https://router.huggingface.co/featherless-ai/v1/completions"
DEFAULT_CHAT_ENDPOINT = "https://router.huggingface.co/v1/chat/completions"
DEFAULT_ENDPOINT_TEMPLATES = [
    "https://api-inference.huggingface.co/models/{model}",
    "https://router.huggingface.co/hf-inference/models/{model}",
]
HTTP_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
TRANSIENT_HTTP_STATUSES = {429, 500, 502, 503, 504}
HF_TOKEN_ALIASES = (
    "HF_TOKEN",
    "HUGGINGFACE_API_KEY",
    "HUGGINGFACEHUB_API_TOKEN",
    "HUGGING_FACE_HUB_TOKEN",
)
AGENT_SERVER_URL_ENV_NAMES = (
    "AGENT_SERVER_URL",
    "AUTOMATION_AGENT_SERVER_URL",
    "RUNTIME_URL",
)
SESSION_KEY_ENV_NAMES = (
    "SESSION_API_KEY",
    "OH_SESSION_API_KEYS_0",
    "LOCAL_BACKEND_API_KEY",
)


def get_secret(name: str) -> str:
    value, _ = get_secret_with_diagnostics(name)
    return value


def first_env(names: tuple[str, ...]) -> tuple[str, str]:
    for env_name in names:
        value = os.environ.get(env_name)
        if value:
            return value, env_name
    return "", ""


def get_secret_with_diagnostics(
    name: str,
    aliases: tuple[str, ...] = (),
) -> tuple[str, dict[str, Any]]:
    env_names = tuple(dict.fromkeys((name, *aliases)))
    value, source_env_name = first_env(env_names)
    diagnostics: dict[str, Any] = {
        "requested_secret": name,
        "env_names_checked": list(env_names),
        "env_present": bool(value),
        "source": f"environment:{source_env_name}" if value else "",
        "agent_server_url_present": False,
        "session_key_present": False,
        "secret_store_attempted": False,
        "secret_store_ok": False,
    }
    if value:
        return value, diagnostics

    server_url, server_url_env_name = first_env(AGENT_SERVER_URL_ENV_NAMES)
    server_url = server_url.rstrip("/")
    session_key, session_key_env_name = first_env(SESSION_KEY_ENV_NAMES)
    diagnostics["agent_server_url_present"] = bool(server_url)
    diagnostics["agent_server_url_env_name"] = server_url_env_name
    diagnostics["session_key_present"] = bool(session_key)
    diagnostics["session_key_env_name"] = session_key_env_name
    if not server_url or not session_key:
        return "", diagnostics

    request = urllib.request.Request(
        f"{server_url}/api/settings/secrets/{name}",
        headers={"X-Session-API-Key": session_key},
    )
    diagnostics["secret_store_attempted"] = True
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            value = response.read().decode().strip()
        diagnostics["secret_store_ok"] = bool(value)
        diagnostics["source"] = "openhands-settings-secret" if value else ""
        return value, diagnostics
    except urllib.error.HTTPError as exc:
        diagnostics["secret_store_http_status"] = exc.code
        return "", diagnostics
    except Exception as exc:
        diagnostics["secret_store_exception"] = type(exc).__name__
        return "", diagnostics


def read_text(path: Path | None) -> str:
    if not path:
        return ""
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def build_prompt(summary: str, spec: str, starter_rtl: str) -> str:
    spec_text = spec.strip() or "No separate spec file was provided."
    starter_text = starter_rtl.strip() or "No starter RTL was provided."
    return textwrap.dedent(
        f"""
        You are ChipCraftX RTLGen, a specialist model for Verilog/SystemVerilog.

        Generate a synthesizable SystemVerilog implementation for this request:

        {summary.strip()}

        Requirements:
        - Implement module sync_fifo.
        - Parameters: WIDTH and DEPTH.
        - Ports: clk, rst_n, wr_en, rd_en, din, dout, full, empty.
        - Use synthesizable SystemVerilog.
        - Implement storage, read/write pointers, occupancy count, full/empty flags.
        - Support simultaneous read and write when legal.
        - Document reset and boundary behavior in RTL comments.
        - Return only the SystemVerilog module, no prose.

        Additional request/spec context:
        {spec_text}

        Starter RTL to replace:
        ```systemverilog
        {starter_text}
        ```
        """
    ).strip()


def build_messages(summary: str, spec: str, starter_rtl: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": textwrap.dedent(
                """
                You are ChipCraft-RTL, an expert Verilog design engineer.
                Generate synthesizable, lint-clean RTL that exactly matches the specification.
                Rules:
                - Output ONLY Verilog/SystemVerilog code.
                - Do not include markdown fences or prose.
                - Prefer Verilog-2001-compatible constructs unless the interface requires SystemVerilog.
                - Use always @(posedge clk) and always @(*) blocks.
                """
            ).strip(),
        },
        {"role": "user", "content": build_prompt(summary, spec, starter_rtl)},
    ]


def inference_url(endpoint_template: str, model: str) -> str:
    quoted_model = urllib.parse.quote(model, safe="/")
    return endpoint_template.format(model=quoted_model)


def endpoint_templates(value: str) -> list[str]:
    templates = [item.strip() for item in re.split(r"[,\n]", value) if item.strip()]
    return templates or DEFAULT_ENDPOINT_TEMPLATES


def call_hf(
    *,
    endpoint_template: str,
    model: str,
    token: str,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    timeout: int,
) -> tuple[str, Any, str]:
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "return_full_text": False,
        },
        "options": {
            "wait_for_model": True,
        },
    }
    url = inference_url(endpoint_template, model)
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": HTTP_USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode(errors="replace")
    data = json.loads(raw)
    return extract_generated_text(data), data, url


def call_huggingface_chat(
    *,
    endpoint: str,
    provider_model: str,
    token: str,
    messages: list[dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    timeout: int,
) -> tuple[str, Any, str]:
    payload = {
        "model": provider_model,
        "messages": messages,
        "max_tokens": max_new_tokens,
        "temperature": temperature,
        "stream": False,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": HTTP_USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode(errors="replace")
    data = json.loads(raw)
    return extract_chat_text(data), data, endpoint


def call_huggingface_completion(
    *,
    endpoint: str,
    model: str,
    token: str,
    prompt: str,
    max_new_tokens: int,
    temperature: float,
    timeout: int,
) -> tuple[str, Any, str]:
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_new_tokens,
        "temperature": temperature,
        "stream": False,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": HTTP_USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode(errors="replace")
    data = json.loads(raw)
    return extract_completion_text(data), data, endpoint


def extract_completion_text(data: Any) -> str:
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                if isinstance(first.get("text"), str):
                    return first["text"]
                message = first.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return message["content"]
    return extract_generated_text(data)


def extract_chat_text(data: Any) -> str:
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return message["content"]
                if isinstance(first.get("text"), str):
                    return first["text"]
    return extract_generated_text(data)


def extract_generated_text(data: Any) -> str:
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            for key in ("generated_text", "summary_text", "text"):
                value = first.get(key)
                if isinstance(value, str):
                    return value
        if isinstance(first, str):
            return first
    if isinstance(data, dict):
        for key in ("generated_text", "text", "output"):
            value = data.get(key)
            if isinstance(value, str):
                return value
        if isinstance(data.get("generated_text"), list):
            return "\n".join(str(item) for item in data["generated_text"])
    return json.dumps(data, indent=2, sort_keys=True)


def extract_systemverilog(text: str) -> str:
    fence = re.search(r"```(?:systemverilog|verilog|sv)?\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
    if fence:
        return fence.group(1).strip() + "\n"

    module = re.search(r"(module\s+sync_fifo\b.*?endmodule)", text, re.IGNORECASE | re.DOTALL)
    if module:
        return module.group(1).strip() + "\n"

    return text.strip() + "\n"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RTL with ChipCraftX via Hugging Face.")
    parser.add_argument("--summary", required=True, help="Short RTL request summary.")
    parser.add_argument("--spec-file", type=Path, default=Path("examples/sync_fifo/fifo_request.md"))
    parser.add_argument("--starter-rtl", type=Path, default=Path("examples/sync_fifo/sync_fifo.sv"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/chipcraftx"))
    parser.add_argument("--model", default=os.getenv("CHIPCRAFTX_HF_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--completion-endpoint",
        default=os.getenv("CHIPCRAFTX_HF_COMPLETION_ENDPOINT", DEFAULT_COMPLETION_ENDPOINT),
        help="OpenAI-compatible Hugging Face Featherless text-completions endpoint.",
    )
    parser.add_argument(
        "--provider-model",
        default=os.getenv("CHIPCRAFTX_HF_ROUTER_MODEL", ""),
        help="HF router model id, optionally with provider/policy suffix.",
    )
    parser.add_argument(
        "--chat-endpoint",
        default=os.getenv("CHIPCRAFTX_HF_CHAT_ENDPOINT", DEFAULT_CHAT_ENDPOINT),
        help="OpenAI-compatible Hugging Face router chat completions endpoint.",
    )
    parser.add_argument(
        "--endpoint-template",
        default=os.getenv(
            "CHIPCRAFTX_HF_ENDPOINT_TEMPLATE",
            ",".join(DEFAULT_ENDPOINT_TEMPLATES),
        ),
        help="Endpoint template containing {model}; comma-separate multiple fallbacks.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=int(os.getenv("CHIPCRAFTX_HF_MAX_NEW_TOKENS", "700")))
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=int(os.getenv("CHIPCRAFTX_HF_RETRIES", "5")))
    parser.add_argument("--retry-sleep", type=float, default=float(os.getenv("CHIPCRAFTX_HF_RETRY_SLEEP", "4")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = args.output_dir / "chipcraftx_metadata.json"
    response_path = args.output_dir / "chipcraftx_raw_response.txt"
    rtl_path = args.output_dir / "chipcraftx_generated_rtl.sv"

    token, secret_diagnostics = get_secret_with_diagnostics("HF_TOKEN", aliases=HF_TOKEN_ALIASES)
    if not token:
        write_json(
            metadata_path,
            {
                "ok": False,
                "model": args.model,
                "error": "HF_TOKEN was not available in the environment or OpenHands secret store.",
                "secret_lookup": secret_diagnostics,
                "timestamp": int(time.time()),
            },
        )
        print(f"CHIPCRAFTX_STATUS=unavailable metadata={metadata_path}")
        return 2

    prompt = build_prompt(
        summary=args.summary,
        spec=read_text(args.spec_file),
        starter_rtl=read_text(args.starter_rtl),
    )
    messages = build_messages(
        summary=args.summary,
        spec=read_text(args.spec_file),
        starter_rtl=read_text(args.starter_rtl),
    )

    generated_text = ""
    raw_data: Any = None
    url = ""
    used_mode = ""
    provider_model = args.provider_model or f"{args.model}:{DEFAULT_PROVIDER_SUFFIX}"
    attempts: list[dict[str, Any]] = []

    max_attempts = max(1, args.retries)
    for attempt_no in range(1, max_attempts + 1):
        try:
            generated_text, raw_data, url = call_huggingface_completion(
                endpoint=args.completion_endpoint,
                model=args.model,
                token=token,
                prompt=prompt,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                timeout=args.timeout,
            )
            used_mode = "hf-featherless-completion"
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            attempts.append(
                {
                    "mode": "hf-featherless-completion",
                    "endpoint": args.completion_endpoint,
                    "model": args.model,
                    "attempt": attempt_no,
                    "http_status": exc.code,
                    "error": body[:2000],
                }
            )
            if exc.code not in TRANSIENT_HTTP_STATUSES or attempt_no == max_attempts:
                break
            time.sleep(args.retry_sleep * attempt_no)
        except Exception as exc:
            attempts.append(
                {
                    "mode": "hf-featherless-completion",
                    "endpoint": args.completion_endpoint,
                    "model": args.model,
                    "attempt": attempt_no,
                    "exception": type(exc).__name__,
                    "error": str(exc),
                }
            )
            if attempt_no == max_attempts:
                break
            time.sleep(args.retry_sleep * attempt_no)

    for attempt_no in range(1, max_attempts + 1):
        if generated_text:
            break
        try:
            generated_text, raw_data, url = call_huggingface_chat(
                endpoint=args.chat_endpoint,
                provider_model=provider_model,
                token=token,
                messages=messages,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                timeout=args.timeout,
            )
            used_mode = "hf-router-chat"
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            attempts.append(
                {
                    "mode": "hf-router-chat",
                    "endpoint": args.chat_endpoint,
                    "provider_model": provider_model,
                    "attempt": attempt_no,
                    "http_status": exc.code,
                    "error": body[:2000],
                }
            )
            if exc.code not in TRANSIENT_HTTP_STATUSES or attempt_no == max_attempts:
                break
            time.sleep(args.retry_sleep * attempt_no)
        except Exception as exc:
            attempts.append(
                {
                    "mode": "hf-router-chat",
                    "endpoint": args.chat_endpoint,
                    "provider_model": provider_model,
                    "attempt": attempt_no,
                    "exception": type(exc).__name__,
                    "error": str(exc),
                }
            )
            if attempt_no == max_attempts:
                break
            time.sleep(args.retry_sleep * attempt_no)

    for template in endpoint_templates(args.endpoint_template):
        if generated_text:
            break
        for attempt_no in range(1, max_attempts + 1):
            write_json(
                metadata_path,
                {
                    "ok": False,
                    "model": args.model,
                    "endpoint": inference_url(template, args.model),
                    "status": "attempting",
                    "attempt": attempt_no,
                },
            )
            try:
                generated_text, raw_data, url = call_hf(
                    endpoint_template=template,
                    model=args.model,
                    token=token,
                    prompt=prompt,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    timeout=args.timeout,
                )
                used_mode = "hf-text-generation"
                break
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                attempts.append(
                    {
                        "mode": "hf-text-generation",
                        "endpoint": inference_url(template, args.model),
                        "attempt": attempt_no,
                        "http_status": exc.code,
                        "error": body[:2000],
                    }
                )
                if exc.code not in TRANSIENT_HTTP_STATUSES or attempt_no == max_attempts:
                    break
                time.sleep(args.retry_sleep * attempt_no)
            except Exception as exc:
                attempts.append(
                    {
                        "mode": "hf-text-generation",
                        "endpoint": inference_url(template, args.model),
                        "attempt": attempt_no,
                        "exception": type(exc).__name__,
                        "error": str(exc),
                    }
                )
                if attempt_no == max_attempts:
                    break
                time.sleep(args.retry_sleep * attempt_no)

    if not generated_text:
        write_json(
            metadata_path,
            {
                "ok": False,
                "model": args.model,
                "provider_model": provider_model,
                "attempts": attempts,
                "secret_source": secret_diagnostics.get("source"),
                "timestamp": int(time.time()),
            },
        )
        last = attempts[-1] if attempts else {"error": "no endpoint attempts were made"}
        status = last.get("http_status") or last.get("exception") or "unknown"
        print(f"CHIPCRAFTX_STATUS=failed metadata={metadata_path} reason={status}")
        return 1

    generated_rtl = extract_systemverilog(generated_text)
    response_path.write_text(generated_text)
    rtl_path.write_text(generated_rtl)
    output_hash = hashlib.sha256(generated_text.encode()).hexdigest()
    rtl_hash = hashlib.sha256(generated_rtl.encode()).hexdigest()
    write_json(
        metadata_path,
        {
            "ok": True,
            "model": args.model,
            "provider_model": provider_model,
            "mode": used_mode,
            "endpoint": url,
            "secret_source": secret_diagnostics.get("source"),
            "raw_response_path": str(response_path),
            "generated_rtl_path": str(rtl_path),
            "raw_response_sha256": output_hash,
            "generated_rtl_sha256": rtl_hash,
            "generated_rtl_bytes": len(generated_rtl.encode()),
            "timestamp": int(time.time()),
        },
    )

    preview = generated_rtl[:800].replace("\n", "\\n")
    print(f"CHIPCRAFTX_STATUS=used model={provider_model} mode={used_mode}")
    print(f"CHIPCRAFTX_METADATA={metadata_path}")
    print(f"CHIPCRAFTX_RTL={rtl_path}")
    print(f"CHIPCRAFTX_RTL_SHA256={rtl_hash}")
    print(f"CHIPCRAFTX_RTL_PREVIEW={preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
