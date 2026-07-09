# Model Routing Policy

Durable policy for future agents working in this repository.

## Default Roles

- Use Sonnet-like orchestration for ambiguous planning, final review, and escalation decisions.
- Use SambaNova Llama 3.3 70B for fast general inference, log triage, small fixes, and repeated short loops.
- Use ChipCraftX RTLGen 7B only as an RTL specialist for Verilog/SystemVerilog generation or repair.
- Use EDA tools as the validation authority.

## Routing Rules

1. Never present model output as validated RTL until at least one deterministic check has run.
2. Prefer lightweight validation first: lint, simulation, then synthesis.
3. If a tool is unavailable, record that as demo evidence rather than hiding it.
4. Keep secrets out of the repo. Use OpenHands secrets or environment configuration.
5. For air-gapped positioning, describe the equivalent private model endpoint or local inference target.

## Competitive Framing

Do not frame the demo as a coding-assistant bakeoff. Frame it as:

> programmable, event-driven engineering automation with intelligent model routing.

