---
name: foundry-model-routing
description: Use for Foundry IT demo requests that need model/tool routing, child automation handoff, air-gapped handling, RTL implementation, or EDA validation policy.
---

# Foundry Model Routing

## Audience Rule

Keep the visible conversation focused on the engineering workflow. Do not expose
internal demo commands, router-shim invocation details, API payload plumbing, or
prompt scaffolding unless the user explicitly asks for debugging detail.

Say that OpenHands routes work to the appropriate model, agent, or tool lane.
When native model-switch evidence is unavailable, describe a route as
"intended", "configured", or "selected by policy"; do not say the specialist
model was actually used.

## Routing Policy

Classify every incoming request before taking action.

- If the request asks for RTL, Verilog, SystemVerilog, VHDL, IP block changes,
  FIFO/register-file/datapath logic, or hardware design repair, route it to the
  RTL specialist lane.
- If the request asks for validation, regression, lint, synthesis, simulation,
  failing logs, or tool output triage, route it to the EDA QA lane.
- If the request includes customer IP, PDK terms, export-controlled content,
  security boundaries, air-gapped needs, or private foundry context, route it to
  the local/private model lane and keep external artifacts minimal.
- If the request is broad planning, impact analysis, or ticket triage, keep it
  in the parent orchestration lane and create child work only after a concrete
  implementation or QA need is identified.
- If the request does not match a known lane, summarize it and ask for human
  triage instead of forcing a child automation.

## Model And Tool Lanes

- Parent orchestration and final judgment: general reasoning model.
- Fast intake, summaries, and log triage: SambaNova Llama 3.3 70B lane.
- RTL generation or repair: ChipCraftX RTLGen 7B specialist lane.
- Sensitive or air-gapped context: customer-private or local model lane.
- Correctness authority: deterministic EDA tools such as Verilator, Icarus
  Verilog, Yosys, Verible, or cocotb.

## Child Automation Handoff

Treat child automations as conditional branches:

- If RTL implementation is needed, create or update a GitHub issue and apply
  `openhands-rtl-build`.
- If a PR needs deterministic validation, apply `openhands-rtl-qa`.
- If extra repository or requirements context is needed before implementation,
  apply `openhands-rtl-context`.
- If human review is needed, leave the PR open and state the review gate.

Do not wait for child automations to finish from the parent. Report the branch
chosen, the label applied, and the next human control point.

## Internal Evidence

The repository includes `scripts/mock_model_router.py` and
`configs/model-routing.yaml` as transparent routing evidence while native SDK /
Canvas routing support is under active development.

Use those files for internal consistency checks when needed, but do not put the
command line or shim mechanics in the audience-facing final response. The final
response should show the route decision, not the implementation detail behind
the route decision.
