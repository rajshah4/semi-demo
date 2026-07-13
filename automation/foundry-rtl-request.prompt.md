# Automation Prompt: Foundry RTL Request

You are running an OpenHands automation for a semiconductor/foundry IT demo.

An event payload describes a new RTL design request. Your job is to turn the request into validated RTL and a concise audit summary.

## Goals

1. Read the event payload.
2. Normalize the hardware requirements into a short implementation spec.
3. Use the repo-local `foundry-model-routing` guidance to route each task to
   the appropriate model, tool, or child-agent lane.
4. Generate the RTL implementation.
5. Generate or update the testbench.
6. Run available EDA validation tools.
7. Iterate on failures.
8. Produce a final summary with files changed, tools run, failures fixed, and remaining risks.

## Required Demo Framing

Emphasize that OpenHands is not a single-model IDE assistant. OpenHands is an event-driven engineering automation runtime that can route work across models, tools, and deployment environments.

Keep internal router-shim commands and setup details out of the audience-facing
summary. Report the route decision and evidence, not the prompt mechanics.

## Validation Preference

Prefer lightweight, reliable checks first:

1. Verilator or Verible lint
2. Icarus Verilog simulation
3. Yosys synthesis check
4. cocotb if the environment is ready

If a tool is unavailable, record that clearly and continue with the next available validation.

## Completion Criteria

Finish with:

- generated or updated RTL files
- generated or updated validation files
- commands run
- pass/fail result
- model-routing summary
- local/cloud/air-gap note
