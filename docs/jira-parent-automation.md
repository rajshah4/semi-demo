# Jira Parent Automation

The demo should start from Jira in the story, even when the live trigger uses GitHub for reliability.

## Why Start From Jira

Foundry IT teams usually treat Jira, ServiceNow, or an internal design portal as the system of record. Starting there makes the demo feel like an enterprise workflow instead of an IDE coding assistant.

## Why There Are Multiple Automations

The repo has several labels because we proved each capability separately:

- `openhands-rtl-sidekick`: parent/child orchestration and routing story
- `openhands-rtl-build`: RTL implementation and PR creation
- `openhands-rtl-qa`: validation and QA evidence
- `openhands-rtl-review`: review posture
- `openhands-rtl-model-switch`: focused proof that native model switching is not exposed in the current runner

For the actual demo, lead with one parent label:

```text
openhands-foundry-parent
```

The parent automation walks through the whole Jira-to-PR path and points to the focused automations only when the audience wants to drill down.

## Demo Flow

1. Jira issue `RTL-1024` requests a synchronous FIFO.
2. Parent automation classifies the work.
3. Router shim shows the route decision.
4. Read-only scouts gather context.
5. RTL work routes to ChipCraftX.
6. Validation routes to the EDA toolchain.
7. Log triage routes to SambaNova.
8. Result lands in GitHub as a PR and human review gate.

## Live Reliability Recommendation

Use Jira in the slide and parent narration. Use GitHub labels as the live trigger unless Jira webhooks are smoke-tested immediately before the demo.

Safe wording:

> Jira is the system-of-record start. For today's live run, this GitHub label is standing in for the Jira webhook so we can focus on the OpenHands workflow: classify, route, implement, validate, and open an auditable PR.
