#!/usr/bin/env python3
"""Transparent model-router shim for the semi demo.

This script is intentionally a mock. It does not call external models and does
not prove native OpenHands model switching. It renders the route decisions and
simulated switch observations that the native model-router PR flow is expected
to make visible.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENT = ROOT / "events" / "new-rtl-block.json"
DEFAULT_TASK = ROOT / "examples" / "rtl_spec" / "fifo_request.md"
DEFAULT_META_PROFILE = ROOT / "configs" / "meta-profile.semi-foundry-router.example.json"


@dataclass(frozen=True)
class RouteDecision:
    step: int
    task: str
    selected: str
    reason: str
    simulated_observation: str


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def read_text_inputs(paths: list[Path], inline_task: str) -> str:
    chunks: list[str] = []
    if inline_task:
        chunks.append(inline_task)
    for path in paths:
        if path.exists():
            chunks.append(path.read_text())
    return "\n\n".join(chunks)


def find_profile(meta_profile: dict[str, Any], needle: str, fallback: str) -> str:
    for route_class in meta_profile.get("classes", []):
        description = str(route_class.get("description", ""))
        if re.search(needle, description, re.IGNORECASE):
            return str(route_class.get("model") or fallback)
    return fallback


def event_summary(event: dict[str, Any]) -> dict[str, str]:
    issue = event.get("issue") if isinstance(event.get("issue"), dict) else {}
    repository = event.get("repository") if isinstance(event.get("repository"), dict) else {}
    return {
        "repository": str(repository.get("full_name") or repository.get("name") or "unknown"),
        "issue": str(issue.get("number") or issue.get("key") or "n/a"),
        "title": str(issue.get("title") or issue.get("summary") or event.get("title") or "unspecified"),
    }


def contains_any(text: str, words: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) for word in words)


def build_route(text: str, event: dict[str, Any], meta_profile: dict[str, Any]) -> list[RouteDecision]:
    classifier = str(meta_profile.get("classifier_model") or "SambaNova-Llama-3.3-70B")
    default_model = str(meta_profile.get("default_model") or "claude-sonnet-4-6")
    rtl_model = find_profile(
        meta_profile,
        r"\bRTL\b|\bVerilog\b|\bSystemVerilog\b|\bVHDL\b",
        "HF-ChipCraftX-RTLGen-7B",
    )
    fast_model = find_profile(
        meta_profile,
        r"\bFast general\b|\blog\b|\bCI\b|\btriage\b",
        "SambaNova-Llama-3.3-70B",
    )
    private_model = find_profile(
        meta_profile,
        r"\bSensitive IP\b|\bair-gapped\b|\bprivate foundry\b|\bmust stay\b|\blocal/private\b",
        "customer-private-model",
    )

    combined = "\n".join([text, json.dumps(event, sort_keys=True)])
    wants_sensitive = contains_any(combined, ["air-gapped", "airgapped", "sensitive", "proprietary", "pdk"])
    wants_rtl = contains_any(
        combined,
        ["rtl", "verilog", "systemverilog", "vhdl", "fifo", "module", "reset", "synthesizable"],
    )
    wants_validation = contains_any(
        combined,
        ["testbench", "lint", "simulate", "synthesis", "synthesize", "verilator", "yosys", "iverilog"],
    )
    wants_log_triage = contains_any(
        combined,
        ["failure", "failed", "error", "log", "trace", "triage", "ci"],
    )

    decisions = [
        RouteDecision(
            step=1,
            task="classify_event",
            selected=classifier,
            reason="Use the classifier profile to map the incoming event to task classes.",
            simulated_observation=f"MOCK_ROUTE_DECISION classifier={classifier} native=false",
        ),
        RouteDecision(
            step=2,
            task="orchestrate_plan",
            selected=default_model,
            reason="Use the default orchestration model for planning, decomposition, and human gates.",
            simulated_observation=f"MOCK_SWITCHLLM_OBSERVATION simulated=true to={default_model}",
        ),
    ]

    if wants_sensitive:
        decisions.append(
            RouteDecision(
                step=len(decisions) + 1,
                task="respect_data_boundary",
                selected=private_model,
                reason="Sensitive or air-gapped terms require the approved local/private profile.",
                simulated_observation=f"MOCK_SWITCHLLM_OBSERVATION simulated=true to={private_model}",
            )
        )

    if wants_rtl:
        decisions.append(
            RouteDecision(
                step=len(decisions) + 1,
                task="generate_or_repair_rtl",
                selected=rtl_model,
                reason="Hardware-design terms route first-pass RTL generation or repair to the RTL specialist.",
                simulated_observation=f"MOCK_SWITCHLLM_OBSERVATION simulated=true to={rtl_model}",
            )
        )

    if wants_validation or wants_rtl:
        decisions.append(
            RouteDecision(
                step=len(decisions) + 1,
                task="validate_with_eda_tools",
                selected="EDA_TOOLCHAIN",
                reason="Correctness should be grounded in Verilator/Icarus/Yosys/Verible results, not model confidence.",
                simulated_observation="MOCK_TOOL_ROUTE simulated=true to=EDA_TOOLCHAIN",
            )
        )

    if wants_log_triage or wants_rtl:
        decisions.append(
            RouteDecision(
                step=len(decisions) + 1,
                task="triage_short_failure_log",
                selected=fast_model,
                reason="Use fast inference for short validation logs and repeated edit/test loops.",
                simulated_observation=f"MOCK_SWITCHLLM_OBSERVATION simulated=true to={fast_model}",
            )
        )

    decisions.append(
        RouteDecision(
            step=len(decisions) + 1,
            task="final_review_and_audit",
            selected=default_model,
            reason="Return to the orchestrator for final judgment, summary, and risk framing.",
            simulated_observation=f"MOCK_SWITCHLLM_OBSERVATION simulated=true to={default_model}",
        )
    )
    return decisions


def render_text(summary: dict[str, str], decisions: list[RouteDecision]) -> str:
    lines = [
        "MODEL_ROUTER_SHIM_START",
        "Native router status: simulated. No live model switch is claimed.",
        f"Repository: {summary['repository']}",
        f"Issue: {summary['issue']}",
        f"Title: {summary['title']}",
        "",
        "Route decisions:",
    ]
    for decision in decisions:
        lines.extend(
            [
                f"{decision.step}. task={decision.task}",
                f"   selected={decision.selected}",
                f"   reason={decision.reason}",
                f"   evidence={decision.simulated_observation}",
            ]
        )
    lines.extend(
        [
            "",
            "Demo wording:",
            "This is a transparent shim for the model-router PR behavior. The current runner did not expose native switch_llm, so this transcript shows the intended route policy without claiming a live SwitchLLMObservation.",
            "MODEL_ROUTER_SHIM_END",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a transparent model-router mock transcript.")
    parser.add_argument("--event", type=Path, default=DEFAULT_EVENT, help="GitHub/Jira-like event JSON")
    parser.add_argument(
        "--input-file",
        action="append",
        type=Path,
        default=[DEFAULT_TASK],
        help="Additional task/spec text; may be passed more than once",
    )
    parser.add_argument("--task", default="", help="Inline task text")
    parser.add_argument("--meta-profile", type=Path, default=DEFAULT_META_PROFILE)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable route decisions")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    event = load_json(args.event)
    meta_profile = load_json(args.meta_profile)
    task_text = read_text_inputs(args.input_file, args.task)
    summary = event_summary(event)
    decisions = build_route(task_text, event, meta_profile)

    if args.json:
        print(
            json.dumps(
                {
                    "native_router_status": "simulated",
                    "summary": summary,
                    "decisions": [decision.__dict__ for decision in decisions],
                },
                indent=2,
            )
        )
        return

    print(render_text(summary, decisions))


if __name__ == "__main__":
    main()
