# GitHub Automation Packages

These prompt packages define the GitHub label-triggered work cells for the
Foundry IT workflow. The Jira-start parent prompt lives in
`automations/jira/rtl-request-parent/`.

## Packages

- `openhands-foundry-parent`: GitHub fallback parent for requests that start in GitHub.
- `openhands-rtl-context`: read-only issue/spec/context scout.
- `openhands-rtl-build`: RTL specialist child that calls ChipCraftX, patches RTL, opens or updates a PR, and hands off to QA.
- `openhands-rtl-qa`: EDA validation child that posts deterministic evidence.
- `openhands-rtl-review`: RTL diff and validation-evidence reviewer.
- `openhands-rtl-model-switch`: optional focused proof package for runtimes that expose native profile switching.

## Trigger Labels

- `openhands-foundry-parent`
- `openhands-rtl-context`
- `openhands-rtl-build`
- `openhands-rtl-qa`
- `openhands-rtl-review`
- `openhands-rtl-model-switch`

Registration helpers are intentionally kept outside this customer-facing repo.
Use your OpenHands automation service or internal deployment tooling to register
these prompt packages.
