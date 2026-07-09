---
name: foundry-sidekick-launcher
description: Launch or describe the visible parent/child conversation demo for foundry RTL workflows. Use when an OpenHands automation receives an RTL request and needs a parent orchestrator plus read-only child scout conversations before implementation.
---

# Foundry Sidekick Launcher

## Overview

Use this skill for the visible parent/child conversation version of the semiconductor demo.

The launcher conversation should unwrap the event, start or describe child conversations, and print a conversation index. It should not implement RTL changes itself.

## Start Marker

Begin the visible response with:

```text
DEMO_STEP 0: Foundry RTL Sidekick Launcher
```

## Expected Demo Shape

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

## Final Response

Print a compact conversation index:

- `timing_summary`
- `parent_conversation`
- `child_conversations`
- `model_route`
- `validation_plan`
- `human_gate`

