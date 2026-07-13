# Semi Demo Change Log

This log preserves the current demo shape, live automation state, and design
decisions so the Foundry IT demo can keep improving without losing context.

## 2026-07-13

### Routing Prompt Cleanup

- Moved detailed model-routing mechanics out of the parent automation prompt and
  into the repo-local skill `.agents/skills/foundry-model-routing/SKILL.md`.
- Simplified the Jira parent automation so it reads like an intake and routing
  decision instead of a setup runbook.
- Changed child-agent handoff language to conditional routing:
  - RTL/design work -> create or update a GitHub issue and apply
    `openhands-rtl-build`.
  - Validation, lint, synthesis, simulation, or log triage -> apply
    `openhands-rtl-qa` to the relevant PR.
  - Sensitive, PDK, customer IP, export-controlled, or air-gapped context ->
    route to a local/private model lane and minimize external artifacts.
  - Unknown lane -> stop at human triage instead of forcing a child automation.
- Removed audience-facing instructions to run `scripts/mock_model_router.py` from
  the parent prompt. The shim remains available as internal evidence, but the
  conversation should show the route decision rather than the mechanics.
- Added the new routing skill to `scripts/preflight_semi_demo.py` so it is
  treated as part of the required demo scaffold.

### Repo And Deployment State

- Pushed commit `cae8d5e` to `rajshah4/semi-demo` on `main`.
- Patched live Rajistics Jira parent automation:
  - Name: `Semi Demo RTL Request Jira Fresh Parent`
  - ID: `df6f72d3-26f4-45a7-a7c1-131cf269c605`
  - Result: enabled, prompt no longer contains `mock_model_router.py`.
- Patched GitHub fallback parent automation:
  - Name: `Semi Demo Foundry Parent Full URL`
  - ID: `53ef1294-078c-4678-9413-9631690dec4b`
  - Result: disabled fallback, prompt no longer contains `mock_model_router.py`.

### Current Main Demo Automations

Keep these enabled for the clean Jira-start flow:

- Jira parent/router:
  `df6f72d3-26f4-45a7-a7c1-131cf269c605`
- RTL build child:
  `4638d8dc-6f54-481e-b49f-968d5da59303`
- EDA QA child:
  `7debee2e-4180-4e63-a9d4-8b10b5fcfe72`

Optional or fallback automations can remain disabled during the main demo:

- GitHub fallback parent:
  `53ef1294-078c-4678-9413-9631690dec4b`
- RTL model switch proof:
  `5162ea58-4c19-4c2c-82bf-cd41ecbf8735`
- RTL review:
  `f0dbda84-1579-4356-a252-4016b6c77a46`
- RTL sidekick:
  `3d384e2c-b9d3-4d91-af28-f3fba25ff2f9`
- RTL context scout:
  `2a5d7237-8112-4efe-94ba-fa9144bc3937`

### Hardwired ChipCraftX Provider Call

The RTL build child now has a real specialist-model path instead of only a
configured/intended route:

- Added `scripts/chipcraftx_generate_rtl.py`, a stdlib-only helper that reads
  `HF_TOKEN`, calls the Hugging Face router chat endpoint, and persists
  generated RTL plus metadata under `artifacts/chipcraftx/`.
- Default specialist provider model:
  `chipcraftx-io/chipcraftx-rtlgen-7b:featherless-ai`.
- Local smoke test on 2026-07-13 succeeded with
  `CHIPCRAFTX_STATUS=used`, mode `hf-router-chat`, and generated RTL SHA256
  `0d71bf99064851247f7711831c6a9f65aae8797541d7ec3bdb1421af41963adb`.
- Updated the RTL build automation prompt so the child agent runs the helper
  before first-pass RTL generation and only claims ChipCraftX usage when the
  helper returns direct evidence.
- Added bounded retries and a 700-token first-draft cap for transient
  hosted-inference errors so the demo is less sensitive to short provider
  hiccups.

Native `switch_llm` is still not available in the Rajistics automation
runtime. For the demo, ChipCraftX evidence comes from the hardwired provider
call and persisted artifact; native model switching remains a future upgrade.

### Latest Clean Proof Run

Jira-start proof run from `KAN-81` after the parent routing-prompt cleanup:

- Jira: https://rajiv-shah.atlassian.net/browse/KAN-81
- Parent/router conversation:
  https://app.replicated.rajistics.com/conversations/776bef67-3e9c-4208-9e49-9954508ac8f2
- RTL build child conversation:
  https://app.replicated.rajistics.com/conversations/5367bd29-89e8-4bb8-8505-add601b03dac
- EDA QA child conversation:
  https://app.replicated.rajistics.com/conversations/8315273d-3bd9-4a01-b99f-db12c03739e3
- GitHub issue:
  https://github.com/rajshah4/semi-demo/issues/17
- Pull request:
  https://github.com/rajshah4/semi-demo/pull/18
- QA evidence comment:
  https://github.com/rajshah4/semi-demo/pull/18#issuecomment-4958442910

Outcome:

- Parent created the GitHub implementation issue and applied
  `openhands-rtl-build`.
- RTL build child opened PR #18 and applied `openhands-rtl-qa`.
- QA child posted a validation report to the PR.
- QA static checks passed. Verilator, Icarus Verilog, and Yosys were not
  installed in that QA environment, so full EDA validation remains a
  toolchain-gated next step.

Jira-start proof run from `KAN-80`:

- Jira: https://rajiv-shah.atlassian.net/browse/KAN-80
- Parent/router conversation:
  https://app.replicated.rajistics.com/conversations/d0d4a489-b929-45d8-babf-b2916b1a5530
- RTL build child conversation:
  https://app.replicated.rajistics.com/conversations/187ae5dd-8738-45b8-8df6-0a28570b93de
- EDA QA child conversation:
  https://app.replicated.rajistics.com/conversations/5c9f03cb-9a51-452a-b3a7-9363da51680d
- GitHub issue:
  https://github.com/rajshah4/semi-demo/issues/15
- Pull request:
  https://github.com/rajshah4/semi-demo/pull/16

Outcome:

- Parent created the GitHub implementation issue and applied
  `openhands-rtl-build`.
- RTL build child opened PR #16 and applied `openhands-rtl-qa`.
- QA child ran deterministic checks and posted a PR comment.
- QA found a useful demo result: Icarus simulation and Yosys synthesis passed,
  while Verilator reported width mismatch warnings that should be fixed before
  merge.

### Demo Story State

The strongest story is now:

1. Jira task is the system-of-record intake.
2. Parent automation classifies the request and selects the route.
3. Labels act as conditional child-agent branches.
4. RTL build child owns implementation and PR creation.
5. QA child owns deterministic EDA validation evidence.
6. Human review remains the merge gate.

### Known Caveats

- Native model switching is not yet available in the Rajistics automation
  environment. ChipCraftX can now be described as used when the hardwired
  provider helper succeeds; SambaNova and native switching should still be
  described as configured or intended unless direct runtime evidence appears.
- The router shim and `configs/model-routing.yaml` are internal evidence for
  the routing policy while SDK/Canvas routing support continues to land.
- The parent conversation should not expose shim commands, setup notes, or
  implementation details unless the user is explicitly debugging the demo.

### Next Improvements

- Run one more Jira ticket after the prompt cleanup to confirm the parent
  conversation no longer over-explains the router shim.
- Consider making the QA child optionally open a follow-up fix PR or comment
  exact patch guidance when Verilator warnings are found.
- Keep the main demo automations list minimal during rehearsal.
