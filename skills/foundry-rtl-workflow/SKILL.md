---
name: foundry-rtl-workflow
description: Use for foundry RTL tasks involving ChipCraftX RTL generation, model-route evidence, GitHub implementation issues, and handoff to EDA validation.
---

# Foundry RTL Workflow

## Core Rule

OpenHands orchestrates the workflow. Specialist models generate or summarize. EDA tools validate.

## Model Roles

- Sonnet-style orchestrator: planning, edits, final judgment
- SambaNova Llama 3.3 70B: fast log triage and repeated small loops
- ChipCraftX RTLGen 7B: Verilog/SystemVerilog generation and repair

## Required Evidence

Every completed run should report:

- event or issue that triggered the run
- model route used
- files changed
- validation commands
- pass/fail status
- unresolved risks

## Skill-Owned Scripts

- `scripts/chipcraftx_generate_rtl.py`: calls the configured ChipCraftX
  Hugging Face provider route and writes generated RTL plus metadata under
  `artifacts/chipcraftx/`.

Run it from the repository root:

```bash
python3 skills/foundry-rtl-workflow/scripts/chipcraftx_generate_rtl.py \
  --summary "<issue title and concise RTL requirements>" \
  --max-new-tokens 700 \
  --retries 5
```

Use the generated RTL as a first draft only. The orchestrator still owns code
review, integration into `rtl/sync_fifo.sv`, validation, PR evidence, and
human-review framing.
