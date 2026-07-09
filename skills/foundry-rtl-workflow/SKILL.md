---
name: foundry-rtl-workflow
description: Use for foundry RTL demo tasks involving model routing, ChipCraftX RTL generation, SambaNova fast inference, EDA validation, and GitHub evidence posting.
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

