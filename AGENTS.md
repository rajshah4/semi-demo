# Agent Instructions

This repository is a semiconductor/foundry IT demo for OpenHands.

## Core Message

OpenHands is a programmable, event-driven engineering automation runtime with intelligent model routing.

## Rules

- Do not commit secrets, tokens, endpoint credentials, PDK licenses, or customer IP.
- Treat EDA tools as the validation authority.
- Use ChipCraftX as an RTL specialist, not as the primary agent brain.
- Use SambaNova for fast general inference and repeated short loops.
- Preserve evidence: commands run, logs summarized, files changed, and model routes used.
- Keep local, cloud, and air-gapped paths explicit.

## Preferred Workflow

1. Read `docs/repo-memory/`.
2. Identify the active work cell.
3. Route models according to `configs/model-routing.yaml`.
4. Run the lightest deterministic validation that proves progress.
5. Summarize results in the system of record.

