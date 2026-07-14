# OpenHands Foundry IT Automation

**Jira request -> model-routed RTL implementation -> EDA validation -> GitHub PR with evidence.**

This repository is a customer-facing reference workflow for using OpenHands in
semiconductor and foundry IT environments. It shows how an engineering request
can start in a system of record, route to the right model and tool lane, produce
real RTL changes, run deterministic validation, and preserve a human review
gate in GitHub.

The point is not that one coding assistant writes better code. The point is:

> OpenHands is a programmable engineering automation runtime that can route
> work across models, agents, tools, and controlled runtime environments.

## What Problem This Solves

Foundry IT teams need agentic automation without losing control of sensitive
design workflows. Common requirements include:

- starting from Jira, GitHub, webhooks, or internal design portals
- routing RTL work to a Verilog/SystemVerilog specialist model
- using fast inference for short logs and repeated triage loops
- keeping sensitive or air-gapped work on approved local infrastructure
- grounding correctness in EDA tools rather than model confidence
- preserving issues, PRs, logs, artifacts, and review decisions

## Primary Workflow

```text
Jira RTL request
  -> parent OpenHands automation classifies and routes the work
  -> parent creates child conversations through Conversation v1
  -> RTL child receives HF_TOKEN as a child-scoped secret and uses ChipCraftX
  -> PR with RTL and validation evidence
  -> QA child runs EDA validation from the repo-local validation skill
  -> human review and merge gate
```

## Work Cells

| Work cell | Trigger | What OpenHands does | Human control point |
| --- | --- | --- | --- |
| **Parent router** | Jira `rtl-request` | Summarizes the ask, applies routing policy, and starts child conversations through Conversation v1 | Scope and system-of-record visibility |
| **RTL specialist** | Parent-created child conversation | Receives `HF_TOKEN` as a child-scoped secret, calls the ChipCraftX helper, integrates RTL, opens or updates a PR | PR review and design acceptance |
| **EDA QA** | Parent-created child conversation after RTL final | Runs static checks plus Verilator, Icarus, and Yosys when installed | Validation acceptance and merge readiness |
| **Review** | GitHub `openhands-rtl-review` label | Reviews RTL diffs, evidence quality, and risk areas | Which findings block merge |

## Model And Tool Routing

| Lane | Example | Purpose |
| --- | --- | --- |
| Parent orchestration | Sonnet-style reasoning model | Planning, decomposition, final judgment |
| Fast inference | SambaNova Llama 3.3 70B | Short summaries, log triage, repeated loops |
| RTL specialist | ChipCraftX RTLGen 7B | Verilog/SystemVerilog first drafts and repair |
| Private boundary | Local/customer model | Sensitive IP, PDK, or air-gapped work |
| Correctness | Verilator, Icarus, Yosys | Deterministic validation evidence |

The RTL child calls the ChipCraftX helper directly so the specialist lane can
persist provider, artifact, and hash evidence when hosted inference succeeds.
That gives the demo a concrete model-use trail while still keeping the workflow
model-agnostic.

## Repository Map

- `automations/jira/` - Jira-start parent automation prompt package.
- `automations/jira/rtl-request-parent/workcells/` - child work-cell prompts for
  Conversation v1 delegated runs.
- `automations/github/` - optional GitHub label-triggered work-cell prompt
  packages for audit/fallback demos.
- `scripts/run_foundry_factory.py` - parent supervisor that creates and monitors
  child app conversations.
- `scripts/openhands_v1_delegate.py` - dependency-free Conversation v1 API helper.
- `skills/foundry-model-routing/` - routing policy and route preview helper.
- `skills/foundry-rtl-workflow/` - RTL implementation policy and ChipCraftX helper.
- `skills/foundry-eda-validation/` - deterministic validation policy and EDA check script.
- `skills/foundry-context-sidekick/` - read-only context scouting instructions.
- `configs/model-routing.yaml` - concrete model and tool routing matrix.
- `configs/meta-profile.semi-foundry-router.example.json` - example model-router profile.
- `examples/sync_fifo/` - sample request, starter RTL, and testbench work cell.
- `docs/` - architecture, model routing, deployment, toolchain, and automation guides.
- `.github/` - issue template, PR template, and label definitions.

## Fast Local Validation

Run the EDA validation skill from the repository root:

```bash
bash skills/foundry-eda-validation/scripts/validate_rtl.sh
```

Preview the route policy without calling external models:

```bash
python3 skills/foundry-model-routing/scripts/model_route_preview.py \
  --event events/jira-rtl-request.json
```

Run the ChipCraftX helper only in an environment where `HF_TOKEN` is available:

```bash
python3 skills/foundry-rtl-workflow/scripts/chipcraftx_generate_rtl.py \
  --summary "Implement the requested synchronous FIFO" \
  --max-new-tokens 700 \
  --retries 5
```

The helper writes generated RTL and metadata under `artifacts/chipcraftx/`,
which is ignored by Git.

## Build Your Own Version

Use this repository as a pattern:

1. Pick the system of record: Jira, GitHub, ServiceNow, or an internal portal.
2. Write one parent prompt that classifies the request and applies policy.
3. Start standalone child conversations through Conversation v1 with narrow
   child prompts and explicit run links in the parent report.
4. Pass child-specific secrets with the v1 `secrets` field rather than printing
   or storing them.
5. Put reusable behavior and scripts inside repo-local skills.
6. Use labels, PRs, comments, and artifacts as the audit trail.
7. Keep secrets in OpenHands or local environment stores, never in Git.

## Security Notes

- Do not commit secrets, tokens, endpoint credentials, PDK licenses, or customer IP.
- Treat EDA tools as the validation authority.
- Use local/private model lanes for sensitive or air-gapped work.
- Keep generated artifacts under ignored directories such as `artifacts/`.
