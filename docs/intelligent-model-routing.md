# Intelligent Model Routing

## Product Hook

This reference workflow highlights intelligent model routing using the OpenHands
SDK and Agent Canvas work:

- SDK PR: https://github.com/OpenHands/software-agent-sdk/pull/3744
- Agent Canvas PR: https://github.com/OpenHands/agent-canvas/pull/1395

The SDK PR adds a `classify_and_switch_llm` tool plus meta-profile storage and API endpoints. The Agent Canvas PR adds a Model Router settings page for creating, editing, activating, and deleting those meta-profiles.

## What A Meta-Profile Means

A meta-profile is a lightweight routing policy:

- `classifier_model`: the model that classifies the current task
- `default_model`: fallback model when no class matches
- `classes`: task descriptions mapped to saved LLM profiles

For this workflow, that lets us show:

> The agent can classify the current engineering task and switch to the best model profile for that step.

## Foundry Meta-Profile

Use `configs/meta-profile.semi-foundry-router.example.json` as the starting point.

Example routing:

- RTL generation or repair -> `HF-ChipCraftX-RTLGen-7B`
- fast log triage or simple code loops -> SambaNova Llama 3.3 70B profile
- complex planning/final review -> Sonnet profile
- sensitive/air-gapped work -> local/private profile

## Lightweight Runtime Path

Even if the full router PRs are not available in a runtime yet, show the same
concept in a lightweight way:

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

## Route Preview

Use the deterministic route preview to explain the routing policy without
depending on a live model call:

```bash
python3 skills/foundry-model-routing/scripts/model_route_preview.py
```

This prints a deterministic route transcript with explicit preview markers. It
is useful for explaining the policy and audit shape before the child workflow
produces model/tool evidence.

Use this wording:

> This is a route-policy preview. It shows the audit shape we want: classify the
> task, select the saved profile, record the route decision, then hand off to
> the right model/tool lane.

## Focused Switch Proof

Use the `openhands-rtl-model-switch` label when the workflow needs a clean proof
separate from RTL generation.

This automation asks the agent to do only three things:

1. check whether `switch_llm` is available
2. switch to `HF-ChipCraftX-RTLGen-7B`
3. switch to `SambaNova-Llama-3.3-70B`

After the run, inspect the conversation event log for `SwitchLLMObservation`.
If the event is present, the workflow can claim live model switching. If it is
absent, keep the claim to saved profiles, routing policy, and the current
runner limitation.

Safe language when the event is absent:

> The profiles and routing policy are configured, but this runner did not expose
> the model-switch tool in the automation conversation. I will show routing as
> policy plus saved profiles, and use the GitHub automation, child
> conversations, and EDA validation as the proof points.

## Talk Track

> A human should not have to manually decide which model is best for every step. OpenHands can encode a model routing policy, classify the current task, and switch to the right saved profile. That is especially valuable in foundry IT, where different steps have different latency, accuracy, cost, and data-boundary requirements.

## Why This Separates OpenHands

Claude Code, Cursor, and Cline can use strong models interactively. The OpenHands angle is broader:

- routes tasks across multiple model providers
- supports specialist models
- uses saved profiles and policy
- can run inside local, cloud, or air-gapped deployments
- keeps the workflow auditable
