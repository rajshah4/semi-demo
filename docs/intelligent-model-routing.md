# Intelligent Model Routing

## Product Hook

This demo should highlight intelligent model routing using the OpenHands SDK and Agent Canvas work:

- SDK PR: https://github.com/OpenHands/software-agent-sdk/pull/3744
- Agent Canvas PR: https://github.com/OpenHands/agent-canvas/pull/1395

The SDK PR adds a `classify_and_switch_llm` tool plus meta-profile storage and API endpoints. The Agent Canvas PR adds a Model Router settings page for creating, editing, activating, and deleting those meta-profiles.

## What A Meta-Profile Means

A meta-profile is a lightweight routing policy:

- `classifier_model`: the model that classifies the current task
- `default_model`: fallback model when no class matches
- `classes`: task descriptions mapped to saved LLM profiles

For this demo, that lets us show:

> The agent can classify the current engineering task and switch to the best model profile for that step.

## Semi Demo Meta-Profile

Use `configs/meta-profile.semi-foundry-router.example.json` as the starting point.

Example routing:

- RTL generation or repair -> `HF-ChipCraftX-RTLGen-7B`
- fast log triage or simple code loops -> SambaNova Llama 3.3 70B profile
- complex planning/final review -> Sonnet profile
- sensitive/air-gapped work -> local/private profile

## Lightweight Live Demo

Even if the full router PRs are not available in the local runtime yet, show the same concept in a lightweight way:

1. Open the Model Router / meta-profile settings when available.
2. Show the `Semi Foundry Router` profile.
3. Trigger the RTL request event.
4. Have OpenHands classify the task.
5. Show or narrate the route:
   - planning goes to Sonnet
   - RTL generation goes to ChipCraftX
   - log triage goes to SambaNova
   - validation goes to EDA tools

The point is not that the classifier is complicated. The point is that OpenHands has a first-class place to encode routing policy.

## Demo Talk Track

> A human should not have to manually decide which model is best for every step. OpenHands can encode a model routing policy, classify the current task, and switch to the right saved profile. That is especially valuable in foundry IT, where different steps have different latency, accuracy, cost, and data-boundary requirements.

## Why This Separates OpenHands

Claude Code, Cursor, and Cline can use strong models interactively. The OpenHands angle is broader:

- routes tasks across multiple model providers
- supports specialist models
- uses saved profiles and policy
- can run inside local, cloud, or air-gapped deployments
- keeps the workflow auditable

