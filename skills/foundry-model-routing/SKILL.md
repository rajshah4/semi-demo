---
name: foundry-model-routing
description: Use for Foundry IT requests that need model/tool routing, child automation handoff, air-gapped handling, RTL implementation, or EDA validation policy.
---

# Foundry Model Routing

## Audience Rule

Keep the visible conversation focused on the engineering workflow. Do not expose
internal commands, route-preview invocation details, API payload plumbing, or
prompt scaffolding unless the user explicitly asks for debugging detail.

Say that OpenHands routes work to the appropriate model, agent, or tool lane.
For this demo, the RTL specialist lane proves model use through the hardwired
ChipCraftX provider call and its durable artifacts. If that provider call does
not succeed, report the provider-call failure without framing it as a native
runtime limitation.

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

The repository includes
`skills/foundry-model-routing/scripts/model_route_preview.py` and
`configs/model-routing.yaml` as transparent routing evidence for the demo.

Use those files for internal consistency checks when needed, but do not put the
command line or preview mechanics in the audience-facing final response. The final
response should show the route decision, not the implementation detail behind
the route decision.

## Hardwired ChipCraftX Evidence

The RTL build child should call
`skills/foundry-rtl-workflow/scripts/chipcraftx_generate_rtl.py` before
first-pass RTL generation. A successful run produces:

- `CHIPCRAFTX_STATUS=used`
- provider `featherless-ai`
- inference mode `hf-featherless-completion`
- `artifacts/chipcraftx/chipcraftx_metadata.json`
- `artifacts/chipcraftx/chipcraftx_generated_rtl.sv`
- a SHA256 hash for the generated RTL

That is enough to say the ChipCraftX model was used. If the helper fails,
report the failure and fall back without claiming ChipCraftX usage.
