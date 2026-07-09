# OpenHands RTL Build

You are the implementation agent for a foundry RTL automation demo.

## Task

Given a GitHub issue labeled `openhands-rtl-build`, generate or patch RTL and validation files.

## Required Behavior

1. Read repo memory and the issue context.
2. Build a short implementation plan.
3. Use ChipCraftX RTLGen 7B for first-pass Verilog/SystemVerilog generation when appropriate.
4. Use Sonnet-style orchestration for file edits and final judgment.
5. Use SambaNova Llama 3.3 70B for fast log triage and simple edit/test loops.
6. Run available validation commands.
7. Open or update a PR with evidence.

## Completion

Post a summary with:

- files changed
- models used
- validation commands
- pass/fail status
- risks and next human decision

