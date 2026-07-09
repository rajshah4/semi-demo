# Replicated Rajistics Setup Status

Last updated: 2026-07-08 America/Chicago

## GitHub

- Repository: https://github.com/rajshah4/semi-demo
- Visibility: private
- Default branch: `main`
- Initial commit: `2d51fb5` (`Create semiconductor demo scaffold`)
- Test issue: https://github.com/rajshah4/semi-demo/issues/1

Labels were applied from `.github/labels.json`, including:

- `rtl-request`
- `openhands-rtl-context`
- `openhands-rtl-build`
- `openhands-rtl-sidekick`
- `openhands-rtl-qa`
- `openhands-rtl-review`

## Rajistics Automations

Host:

- `https://app.replicated.rajistics.com`

Registered prompt-preset automations:

| Automation | ID | Trigger |
|---|---|---|
| Semi Demo RTL Context Scout | `2a5d7237-8112-4efe-94ba-fa9144bc3937` | GitHub `issues.labeled`, label `openhands-rtl-context` |
| Semi Demo RTL Build | `4638d8dc-6f54-481e-b49f-968d5da59303` | GitHub `issues.labeled`, label `openhands-rtl-build` |
| Semi Demo RTL Sidekick | `3d384e2c-b9d3-4d91-af28-f3fba25ff2f9` | GitHub `issues.labeled`, label `openhands-rtl-sidekick` |
| Semi Demo RTL QA | `7debee2e-4180-4e63-a9d4-8b10b5fcfe72` | GitHub `pull_request.labeled`, label `openhands-rtl-qa` |
| Semi Demo RTL Review | `f0dbda84-1579-4356-a252-4016b6c77a46` | GitHub `pull_request.labeled`, label `openhands-rtl-review` |

## Live Smoke Test

Trigger:

- Created GitHub issue #1 with `rtl-request`.
- Added label `openhands-rtl-sidekick`.

Result:

- Automation run: `85685cd7-2c84-485c-8e55-e9f9fad4d4b0`
- Status: `COMPLETED`
- Conversation: `a90c4117-d159-4410-a93f-3397325d683d`
- Conversation URL: https://app.replicated.rajistics.com/conversations/a90c4117-d159-4410-a93f-3397325d683d
- Repo search confirmed `rajshah4/semi-demo` is visible to the Rajistics app API.

The completed conversation produced the expected launcher summary:

- event summary for GitHub issue #1
- child conversation plan
- model route table
- validation plan
- evidence/audit framing

## Secret Status

Local source file:

- `/Users/rajiv.shah/Code/install_replicate/.env`

Presence check, values not printed:

| Secret/env name | Local `.env` status | Demo use |
|---|---|---|
| `OPENHANDS_API_KEY_ORG` | present | Register/list Rajistics automations |
| `GITHUB_TOKEN` | present | Needed for custom launcher scripts that call GitHub directly |
| `HF_API_KEY` | present | Can be used for ChipCraftX/Hugging Face calls |
| `HF_TOKEN` | missing | Recommended alias for HF tooling and parity with local Canvas |
| `SAMBANOVA_API_KEY` | missing | Needed if the demo calls SambaNova directly or creates a direct SambaNova profile |
| `ANTHROPIC_API_KEY` | present | Available locally; Rajistics base LLM already worked for the smoke test |
| `JIRA_API_TOKEN` | present | Jira direct workflow, not required for this GitHub smoke test |
| `JIRA_API_BASE_URL` | present | Jira direct workflow |
| `JIRA_SITE_URL` | present | Jira direct workflow |
| `JIRA_AUTH_MODE` | present | Jira direct workflow |
| `JIRA_SERVICE_ACCOUNT_EMAIL` | present | Jira traceability |
| `JIRA_WEBHOOK_SECRET` | present | Jira direct webhook |
| `LMNR_PROJECT_API_KEY` | present | Laminar analytics/tracing |

## What Can Be Reused

Reuse from the existing Rajistics/SDLC setup:

- `OPENHANDS_API_KEY_ORG`
- GitHub integration/App path, proven by issue label triggering the automation
- existing default LLM configuration, proven by completed conversation
- Jira secrets and `jira-direct` pattern if the demo moves from GitHub to Jira
- Laminar key if analytics/traces are part of the demo

## What To Add Or Recreate

Add or verify in Rajistics before the full model-routed demo:

1. `HF_TOKEN`
   - Local `.env` has `HF_API_KEY`, but `HF_TOKEN` is missing.
   - Recommended: create `HF_TOKEN` as an alias to the same Hugging Face token, or update demo code to look for both `HF_TOKEN` and `HF_API_KEY`.

2. `SAMBANOVA_API_KEY`
   - Missing locally.
   - Needed for direct SambaNova fast-inference calls or a saved SambaNova LLM profile unless Rajistics already has SambaNova configured through LiteLLM/admin config.

3. ChipCraftX profile on Rajistics
   - Local Canvas has `HF-ChipCraftX-RTLGen-7B`.
   - Need equivalent Rajistics profile or helper tool before showing live ChipCraftX generation.

4. Model Router/meta-profile support
   - Current local Agent Canvas did not expose `/api/meta-profiles`.
   - For a live router UI demo, use a build with OpenHands SDK PR #3744 and Agent Canvas PR #1395, or keep this part as lightweight config/policy narration.

## API Caveat

Automation APIs are reachable with:

```text
Authorization: Bearer <OPENHANDS_API_KEY_ORG>
```

App conversation APIs are reachable with:

```text
X-Access-Token: <OPENHANDS_API_KEY_ORG>
```

The frontend route `/api/conversations/...` returned HTML on Rajistics; use `/api/v1/...` app-server endpoints for conversation inspection.

