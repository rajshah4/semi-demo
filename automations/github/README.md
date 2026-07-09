# GitHub Automation Packages

These prompt packages mirror the SDLC automation demo pattern and adapt it to foundry/RTL workflows.

## Packages

- `openhands-rtl-context`: scout the issue/spec and post a routing/context report
- `openhands-rtl-build`: generate or patch RTL and open/update implementation work
- `openhands-rtl-qa`: run EDA validation and post evidence
- `openhands-rtl-review`: review RTL diffs and test coverage
- `openhands-rtl-model-switch`: run a tiny proof that checks whether `switch_llm` is available and produces direct switch evidence

## Trigger Labels

- `openhands-rtl-context`
- `openhands-rtl-build`
- `openhands-rtl-qa`
- `openhands-rtl-review`
- `openhands-rtl-model-switch`

## Registration

Dry-run all prompt-preset payloads:

```bash
python3 scripts/register_github_automations.py --dry-run
```

Register one package:

```bash
python3 scripts/register_github_automations.py --apply --only openhands-rtl-model-switch
```
