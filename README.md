# Semi Demo

Demo workspace for showing OpenHands as an agentic engineering platform for semiconductor and foundry IT workflows.

The core message is not "one coding assistant writes better code." The message is:

> OpenHands routes engineering work to the right model, runs the right tools, and executes auditable workflows in controlled local, cloud, or air-gapped environments.

## Demo Thesis

Foundry IT teams need more than IDE autocomplete. They need controlled automation that can:

- start from an event such as a ticket, issue, webhook, or design request
- choose the right model for each task
- call specialist models for RTL and Verilog work
- use fast private inference for repeated agent loops
- run EDA tools as the source of truth
- preserve traces, logs, outputs, and review points
- work across local, cloud, and air-gapped deployments

## Primary Demo

**Webhook to validated RTL**

1. A new RTL block request arrives from a webhook-like event.
2. OpenHands starts an automation workflow.
3. The orchestrator uses Sonnet for planning and task decomposition.
4. The router calls SambaNova Llama 3.3 70B for fast general coding/log analysis.
5. The router calls ChipCraftX RTLGen 7B for Verilog/RTL generation or repair.
6. OpenHands runs EDA tools such as Verilator, Yosys, Verible, Icarus, or cocotb.
7. The workflow patches failures, reruns validation, and produces an auditable summary.

## Competitive Positioning

Claude Code, Cursor, and Cline are strong interactive coding assistants. This demo should position OpenHands differently:

> OpenHands is a programmable agent runtime for enterprise engineering workflows.

The strongest differentiators to show:

- intelligent model routing
- event-driven automations
- subagents and multi-conversation workflows
- toolchain-grounded validation
- pre-baked runtime images
- local-to-cloud-to-air-gapped deployment options
- auditable traces and policy controls

## Repository Map

- `docs/demo-script.md` - narrator flow and talk track
- `docs/live-demo-script.md` - presenter-ready demo script with critical feature callouts
- `docs/architecture.md` - system architecture and routing diagram
- `docs/work-cells.md` - SDLC-demo-inspired work cells for foundry/RTL
- `docs/parent-child-conversations.md` - parent orchestrator and child conversation sidekick pattern
- `docs/intelligent-model-routing.md` - how SDK/Canvas model-router PRs fit the demo
- `docs/model-routing.md` - model roles and routing rules
- `docs/local-cloud-airgap.md` - deployment tradeoffs
- `docs/toolchain-image.md` - what to pre-bake into an EDA image
- `docs/automation-entrypoint.md` - webhook and polling automation starting points
- `docs/inspiration.md` - outside references and demo ideas to mine later
- `docs/repo-memory/` - durable agent memory and policy notes
- `automations/github/` - label-triggered GitHub automation prompt packages
- `.github/` - issue template, PR template, and demo labels
- `configs/model-routing.yaml` - concrete routing matrix
- `configs/meta-profile.semi-foundry-router.example.json` - OpenHands Model Router meta-profile example
- `workflows/foundry-rtl-workflow.yaml` - demo workflow definition
- `workflows/foundry-rtl-sidekick-workflow.yaml` - visible parent/child conversation workflow
- `events/new-rtl-block.json` - sample incoming event
- `automation/foundry-rtl-request.prompt.md` - prompt preset draft for OpenHands Automation
- `automations/github/openhands-rtl-sidekick/` - visible parent/child sidekick prompt package
- `automation/preset-payload.example.json` - sample automation API payload, no secrets
- `examples/rtl_spec/fifo_request.md` - first RTL block request
- `scripts/simulate-event.sh` - local dry-run helper for the event payload

## Current Status

This is a scaffold, not yet the final runnable demo. Next work:

- wire the event into a local OpenHands/Agent Canvas conversation
- check whether the local runtime includes SDK PR #3744 and Canvas PR #1395
- wire a parent/child conversation launcher modeled on `sdlc-sidekick-launcher`
- add a helper tool that calls the ChipCraftX HF profile as an RTL specialist
- add a SambaNova profile smoke test and timing run
- choose the first EDA validation path, likely Verilator or Icarus first
- make the local and cloud variants explicit
- borrow registration/preflight patterns from `rajshah4/sdlc-automation-github-demo`

## Fast Local Validation

```bash
python3 scripts/preflight_semi_demo.py
python3 scripts/register_github_automations.py --dry-run
scripts/simulate-event.sh
```
