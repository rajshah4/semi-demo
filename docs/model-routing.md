# Model Routing

## Routing Principle

Route by task, not by brand.

Each model gets a job that matches its strengths:

- **Sonnet**: orchestration, planning, hard reasoning, cross-file judgment
- **SambaNova Llama 3.3 70B**: fast general inference, repeated edit/test loops, log summarization
- **ChipCraftX RTLGen 7B**: RTL/Verilog generation and repair
- **Local/private model**: sensitive source, air-gapped execution, policy-constrained paths

## OpenHands Model Router Hook

The OpenHands SDK PR `OpenHands/software-agent-sdk#3744` adds a `classify_and_switch_llm` tool and meta-profile APIs. The Agent Canvas PR `OpenHands/agent-canvas#1395` adds the UI for managing those meta-profiles.

This lets the workflow show model routing as a first-class OpenHands concept:

1. define a meta-profile with classifier/default/classes
2. activate it in Canvas
3. let the agent classify the current task
4. switch to the saved profile that best matches the work

See `configs/meta-profile.semi-foundry-router.example.json`.

## Example Routing Rules

| Task | Preferred Route | Why |
|---|---|---|
| Interpret incoming ticket/spec | Sonnet | Ambiguity and planning |
| Generate first Verilog module | ChipCraftX | Domain specialization |
| Summarize long simulation logs | SambaNova | Fast iteration |
| Patch straightforward syntax errors | SambaNova | Low-latency edits |
| Repair functional RTL behavior | Sonnet + ChipCraftX | Planning plus domain code |
| Validate code | EDA tools | Deterministic source of truth |
| Sensitive internal IP | Local/private model | Data boundary |

## Customer Claim

> A coding agent becomes much more valuable when it can choose the right model for each step of the workflow.

## Evidence Ladder

Use the strongest claim that the current runtime actually proves:

1. `SwitchLLMObservation` found in the conversation log: claim live model switching.
2. Saved profiles plus automation prompt route found, but no switch observation: claim configured routing policy and explain the runner gap.
3. No profile access: show the repo policy and keep routing as reference design.

The `openhands-rtl-model-switch` automation exists to test the first rung without mixing in code generation, branches, PRs, or EDA setup.

## Caveat

ChipCraftX should be shown as an RTL specialist, not as the primary agent brain. The primary agent should orchestrate, call tools, read logs, and decide when to invoke ChipCraftX.
