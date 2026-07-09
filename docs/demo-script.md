# Demo Script

## Title

From Foundry Ticket to Validated RTL: OpenHands as a Model-Routed Engineering Automation Runtime

## Opening Frame

Do not open with "AI writes Verilog." Open with the foundry IT problem:

> Foundry teams do not just need code generation. They need controlled, auditable automation that can run inside approved environments, use approved models, and validate every change with the real engineering toolchain.

## The Three Beats

### 1. Event-Driven Workflow

Start with a realistic trigger:

- GitHub issue labeled `rtl-request`
- Jira ticket for a new block
- custom webhook from an internal design portal
- CI failure on an RTL branch

Talk track:

> The workflow starts from an event, not from a developer typing in an IDE. That matters because enterprise teams want repeatable automations tied to their systems of record.

### 2. Intelligent Model Routing

Show that OpenHands can use multiple models in one workflow:

- Sonnet for orchestration and hard reasoning
- SambaNova Llama 3.3 70B for fast general coding, summaries, and log triage
- ChipCraftX RTLGen 7B for Verilog/RTL generation and repair
- local/private model for sensitive or air-gapped paths

Talk track:

> The agent should not have one brain for every task. It should route each step to the model that best fits the work, latency, cost, data boundary, and specialization requirement.

Product hook:

> This maps directly to the OpenHands Model Router work: a meta-profile defines a classifier model, a default model, and task classes that map to saved LLM profiles. The agent can call `classify_and_switch_llm` to move the conversation to the right profile.

### 3. Toolchain-Grounded Validation

Run the actual checks:

- lint/parse
- simulate
- synthesize
- format
- summarize results

Talk track:

> The model proposes. The EDA tools judge. The agent loops until the workflow reaches a known engineering state.

## Suggested Live Flow

1. Show `events/new-rtl-block.json`.
2. Trigger or simulate the automation.
3. Open the parent launcher conversation.
4. Show the child conversation index.
5. Click into one read-only scout conversation.
6. Return to the parent/main implementation conversation.
7. Show the model routing decision.
8. Generate initial RTL with ChipCraftX.
9. Run a testbench or lint command.
10. Let a failure happen.
11. Show SambaNova or Sonnet triaging the failure quickly.
12. Patch the RTL.
13. Rerun validation.
14. Show final summary and audit trace.

## Closing Line

> Claude Code and Cursor are great developer assistants. This is different: OpenHands is a model-flexible automation runtime for enterprise engineering workflows.
