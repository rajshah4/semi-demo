# Jira Parent Automation

The workflow starts from Jira. A Jira Task with the `rtl-request` label triggers
the parent OpenHands automation through the `jira-direct` webhook.

## Why Start From Jira

Foundry IT teams usually treat Jira, ServiceNow, or an internal design portal
as the system of record. Starting there makes the workflow feel like enterprise
automation instead of an IDE coding assistant.

## Why There Are Multiple Automations

The repo has several labels because we proved each capability separately:

- `openhands-rtl-sidekick`: parent/child orchestration and routing story
- `openhands-rtl-build`: RTL implementation and PR creation
- `openhands-rtl-qa`: validation and QA evidence
- `openhands-rtl-review`: review posture
- `openhands-rtl-model-switch`: optional focused proof package for runtimes that
  expose native profile switching

For the main path, lead with one Jira label:

```text
rtl-request
```

The parent automation walks through the Jira-to-PR path and delegates to
focused child conversations through the OpenHands Conversation v1 API.

## Workflow

1. A Jira Task requests a synchronous FIFO and carries label `rtl-request`.
2. Parent automation classifies the work.
3. Routing policy selects the model, tool, or child-agent lane.
4. Parent starts Child Agent 1: RTL specialist as a standalone Conversation v1
   child.
5. The RTL child receives `HF_TOKEN` through the child runtime secret endpoint
   before the child run starts.
6. RTL child calls the ChipCraftX lane when available, patches RTL, runs
   validation, and opens or updates a PR.
7. Parent starts Child Agent 2: Verification / EDA QA after the RTL child
   finishes.
8. QA child runs deterministic EDA checks where available and uses the SambaNova lane for fast validation-log triage when routing is available.
9. Result lands in GitHub as a PR, QA evidence, and human review gate.

## Reliability Recommendation

Use Jira as the primary system-of-record trigger. Keep the GitHub
`openhands-foundry-parent` label as a fallback if the Jira webhook path is
unavailable.

Safe wording:

> Jira is the system-of-record start. The `rtl-request` label launches the parent OpenHands workflow. The parent routes the work, delegates RTL implementation to a specialist child, delegates validation to a QA child, and keeps the GitHub PR plus evidence trail visible for human review.
