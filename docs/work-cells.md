# Work Cells

This demo borrows the work-cell pattern from `rajshah4/sdlc-automation-github-demo` and adapts it to semiconductor/foundry IT.

## Why Work Cells

Work cells make the automation boundary visible. A human applies a label or creates an event, OpenHands runs a bounded workflow, and evidence returns to the same system of record.

## Proposed GitHub Work Cells

| Work cell | Trigger label | What OpenHands does | Human control point |
|---|---|---|---|
| RTL Context Scout | `openhands-rtl-context` | Reads the issue/spec, repo memory, existing RTL patterns, and available toolchain; posts a short context/routing plan | Decide whether to build, QA, or ask for clarification |
| RTL Build | `openhands-rtl-build` | Generates or patches RTL, writes/updates tests, runs first validation loop | Review branch/PR scope |
| EDA QA | `openhands-rtl-qa` | Runs deterministic EDA checks, summarizes failures, adds missing tests where safe | Decide whether validation is sufficient |
| RTL Review | `openhands-rtl-review` | Reviews RTL diff for resets, widths, synthesizability, test gaps, and style | Decide which findings block merge |
| Visible Sidekick | `openhands-rtl-sidekick` | Parent launcher creates a conversation index, child scouts gather context, main agent implements | Decide whether to continue from scout findings |

## Why This Competes Well

Claude Code, Cursor, and Cline can help an individual developer inside an editor. Work cells show a different category:

> Human-approved events launch repeatable engineering workflows with model routing, toolchain validation, and auditable outputs.

## Demo Label Flow

1. Create issue with `rtl-request`.
2. For the visible multi-conversation demo, apply `openhands-rtl-sidekick`.
3. Parent conversation posts child conversation index.
4. Child scouts gather spec, repo, toolchain, and model-route context.
5. Main implementation consumes scout briefs and creates RTL/tests.
6. Apply `openhands-rtl-qa` to run validation.
7. Apply `openhands-rtl-review` before merge.

For a shorter live demo, combine build, QA, and review into one workflow and show the work cells as the production pattern.
