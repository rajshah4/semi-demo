---
name: foundry-sidekick-launcher
description: Launch or describe the visible parent/child conversation workflow for foundry RTL requests. Use when an OpenHands automation receives an RTL request and needs a parent orchestrator plus read-only child scout conversations before implementation.
---

# Foundry Sidekick Launcher

## Overview

Use this skill for the visible parent/child conversation version of the
semiconductor workflow.

The launcher conversation should unwrap the event, start or describe child conversations, and print a conversation index. It should not implement RTL changes itself.

## Start Marker

Begin the visible response with:

```text
DEMO_STEP 0: Foundry RTL Sidekick Launcher
```

## Expected Workflow Shape

- Step 0: parent launcher unwraps the event and prints the index.
- Step 2A: spec scout normalizes requirements and ambiguity.
- Step 2B: RTL repo scout finds existing modules, tests, and patterns.
- Step 2C: toolchain scout checks validation commands and image gaps.
- Step 2D: model route scout recommends Sonnet/SambaNova/ChipCraftX/local routing.
- Step 3: main implementation conversation consumes scout briefs, generates RTL/tests, and runs validation.
- Step 4: QA/review conversation posts evidence and leaves human review intact.

## Hard Rules

- Do not implement the RTL change in Step 0.
- Scouts are read-only.
- Do not print secrets, tokens, license paths, or customer IP.
- Do not rerun a launcher after child conversations have started unless the human approves duplicate conversations.
- The final response must include child conversation links when available.

## Conversation v1 Child Handoff

For child conversations that need runtime secrets, pass those secrets when the
Conversation v1 app conversation is created:

1. Create the child app conversation with `initial_message.run: true`.
2. Include only the required child secrets in the create payload, for example
   `HF_TOKEN` for the RTL specialist child.
3. In terminal commands that need a secret-backed environment variable,
   reference the variable explicitly without printing it, for example
   `HF_TOKEN="${HF_TOKEN:-}" python3 ...`.

For this handoff path, a direct read from `/api/settings/secrets/{name}` is not
the proof point; verify through the child execution environment or the
specialist helper's model-use metadata.

Keep children as standalone conversations; do not set `parent_conversation_id`.
Never print secret values, authorization headers, encrypted settings, or raw
environment dumps while debugging this flow.

## Final Response

Print a compact conversation index:

- `timing_summary`
- `parent_conversation`
- `child_conversations`
- `model_route`
- `validation_plan`
- `human_gate`
