# Repo-Local Skills

These skills keep reusable workflow behavior and skill-owned scripts close
together. Agents should prefer these skill instructions over ad hoc commands.

| Skill | Owns | Key scripts |
| --- | --- | --- |
| `foundry-model-routing` | Model-route policy, evidence rules, and route previews | `scripts/model_route_preview.py` |
| `foundry-rtl-workflow` | RTL implementation flow and ChipCraftX specialist calls | `scripts/chipcraftx_generate_rtl.py` |
| `foundry-eda-validation` | Static checks and optional EDA-backed validation | `scripts/validate_rtl.sh` |
| `foundry-context-sidekick` | Read-only request/repo/toolchain scouting | none |
| `foundry-sidekick-launcher` | Parent/child conversation shape | none |

Run skill scripts from the repository root so their default paths resolve to
`configs/`, `events/`, and `examples/`.
