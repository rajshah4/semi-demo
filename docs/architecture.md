# Architecture

## System Shape

```mermaid
flowchart LR
  event["Event source<br/>GitHub, Jira, CI, design portal"] --> automation["OpenHands Automation Server"]
  automation --> orchestrator["Parent OpenHands conversation<br/>orchestration + audit index"]
  orchestrator --> sidekickA["Child conversation<br/>spec scout"]
  orchestrator --> sidekickB["Child conversation<br/>repo scout"]
  orchestrator --> sidekickC["Child conversation<br/>toolchain scout"]
  orchestrator --> router["Model router<br/>meta-profile + classify_and_switch_llm"]
  router --> fast["SambaNova<br/>Llama 3.3 70B<br/>fast general inference"]
  router --> rtl["ChipCraftX RTLGen 7B<br/>RTL specialist"]
  router --> local["Local/private model<br/>air-gapped paths"]
  orchestrator --> tools["EDA toolchain<br/>Verilator, Yosys, Verible, cocotb"]
  tools --> results["Validation results<br/>logs, artifacts, summary"]
  results --> orchestrator
  orchestrator --> output["Ticket/PR/update<br/>auditable trace"]
```

## Responsibilities

OpenHands Automation Server:

- receives event or cron trigger
- launches the workflow
- passes event context
- records run status

OpenHands Agent:

- plans the task
- creates or edits files
- invokes tools
- decides when to route to specialist models
- posts the final result

Model Router:

- selects model by task type
- respects data boundary and deployment mode
- uses latency-sensitive models for repeated loops
- uses specialist models for domain generation

EDA Toolchain:

- validates syntax, lint, simulation, synthesis, and formatting
- acts as the source of truth
- produces logs that the agent can triage

## Why This Is Different

This is not a single assistant inside an editor. It is a workflow runtime:

- model-agnostic
- toolchain-aware
- event-triggered
- policy-aware
- deployable locally, in cloud, or in an air-gapped environment
