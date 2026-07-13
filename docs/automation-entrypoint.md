# Automation Entrypoint

## Starting Point

The workflow should start from an event, not from an interactive prompt.

Good event options:

- GitHub issue opened with label `rtl-request`
- GitHub comment mentioning `@openhands`
- Jira ticket created for a new RTL block
- custom webhook from an internal design-request portal
- CI failure on an RTL branch

## Local Pattern

For a local laptop or private network, external webhooks may not be able to
reach the automation service. Use one of these instead:

- manual dispatch from the OpenHands automation UI/API
- cron polling against GitHub/Jira for new matching events

## Cloud Pattern

For cloud, use a real event trigger:

- GitHub `issues.opened`
- GitHub `issue_comment.created`
- GitHub `pull_request.labeled`
- custom webhook source for an internal portal

## Automation Prompt Package

Use `automations/jira/rtl-request-parent/prompt.md` as the Jira-start parent
prompt package. Use `automations/github/` for GitHub label-triggered child work
cells.

It should instruct the agent to:

1. read the event payload
2. classify the request
3. route planning to the orchestration model
4. route RTL generation/repair to ChipCraftX
5. route fast log triage to SambaNova
6. run validation tools
7. post a final summary

## Deployment Rule

Do not put secrets in this repo. Model API keys should live in OpenHands secrets or the target automation environment.
