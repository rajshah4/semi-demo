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

## Fresh Smoke Test After Model Profiles

Trigger:

- Created GitHub issue #2 with `rtl-request`.
- Added label `openhands-rtl-sidekick`.

Result:

- Automation run: `a96dad55-99be-493b-904e-f8d7fdf6aad7`
- Status: `COMPLETED`
- Conversation: `a9d99f2c-d66c-419b-83a8-7dcd42412451`
- Conversation URL: https://app.replicated.rajistics.com/conversations/a9d99f2c-d66c-419b-83a8-7dcd42412451

The completed conversation produced the expected sidekick markers:

- `DEMO_STEP 0: Foundry RTL Sidekick Launcher`
- event summary
- child conversation plan
- model route table
- validation plan
- evidence/audit framing
- SambaNova and ChipCraftX references

## Hard-Mode Build And QA Dress Rehearsal

Trigger:

- Created GitHub issue #3 with `rtl-request`.
- Added label `openhands-rtl-build`.

Build result:

- Automation run: `adc32b67-182f-45d9-ab02-2e6797a968df`
- Status: `COMPLETED`
- Conversation: `2cac15c3-7dae-47e8-bf85-d51238dd6a60`
- Conversation URL: https://app.replicated.rajistics.com/conversations/2cac15c3-7dae-47e8-bf85-d51238dd6a60
- Pull request: https://github.com/rajshah4/semi-demo/pull/4

Build evidence:

- OpenHands created branch `rtl/sync-fifo-implementation-issue-3`.
- OpenHands replaced the starter `rtl/sync_fifo.sv` with a FIFO implementation.
- Static validation passed with `bash scripts/validate_rtl.sh`.
- The first generated RTL had two demo-quality issues:
  - it embedded an "intended model" claim in source comments
  - it indexed `DEPTH` like a vector
- Follow-up commit `d25667d` tightened the RTL implementation.
- Main branch commit `50c5763` tightened the build prompt so future runs cannot claim model use without `switch_llm` evidence.

Model-routing caveat:

- Saved profiles are present for `HF-ChipCraftX-RTLGen-7B` and `SambaNova-Llama-3.3-70B`.
- The build conversation included profile names and `switch_llm` instructions, but inspection did not find a successful `SwitchLLMObservation`.
- Treat this run as evidence for event-driven build automation plus validation, not as proof that the model-switch tool was exercised.

QA trigger:

- Added label `openhands-rtl-qa` to PR #4.

QA result:

- Automation run: `0911b45d-24d0-4415-b87e-aeb0a421b5fa`
- Status: `COMPLETED`
- Conversation: `270dd4bd-67ef-4f82-94c9-1c4fa4401b9d`
- Conversation URL: https://app.replicated.rajistics.com/conversations/270dd4bd-67ef-4f82-94c9-1c4fa4401b9d
- QA comment: https://github.com/rajshah4/semi-demo/pull/4#issuecomment-4920910356

QA evidence:

- Checked out PR branch commit `d25667d`.
- Ran `bash scripts/validate_rtl.sh rtl/sync_fifo.sv tb/sync_fifo_tb.sv`.
- Static checks passed.
- Verilator, Icarus Verilog, and Yosys were not installed in the runtime, so EDA checks were skipped.

Remaining hard-mode gap:

- To claim full EDA validation, use a runtime image with Verilator, Icarus Verilog, and/or Yosys preinstalled.
- To claim live model routing, rerun after confirming `switch_llm` is available to the automation agent and verify a `SwitchLLMObservation` event.

## Secret Status

Local source file:

- `/Users/rajiv.shah/Code/install_replicate/.env`

Presence check, values not printed:

| Secret/env name | Local `.env` status | Demo use |
|---|---|---|
| `OPENHANDS_API_KEY_ORG` | present | Register/list Rajistics automations |
| `GITHUB_TOKEN` | present | Needed for custom launcher scripts that call GitHub directly |
| `HF_TOKEN` | present | Hugging Face token for ChipCraftX/HF inference |
| `SAMBANOVA_API_KEY` | present | SambaNova API key for fast inference |
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

Added in Rajistics via `/api/v1/secrets` on 2026-07-08:

- `HF_TOKEN`
- `SAMBANOVA_API_KEY`

Added/verified LLM profile setup:

1. ChipCraftX profile on Rajistics
   - Local Canvas has `HF-ChipCraftX-RTLGen-7B`.
   - Rajistics now also has `HF-ChipCraftX-RTLGen-7B`.
   - Model: `huggingface/featherless-ai/chipcraftx-io/chipcraftx-rtlgen-7b`.
   - Readback shows `api_key_set: true`; the stored key value was not printed.

2. SambaNova LLM profile on Rajistics
   - The `SAMBANOVA_API_KEY` secret is now present.
   - Rajistics now has `SambaNova-Llama-3.3-70B`.
   - Model: `openai/Meta-Llama-3.3-70B-Instruct`.
   - Base URL: `https://api.sambanova.ai/v1`.
   - Readback shows `api_key_set: true`; the stored key value was not printed.

3. Model Router/meta-profile support
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
