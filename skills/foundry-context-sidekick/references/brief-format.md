# Foundry Context Brief Format

Use this format for read-only scout outputs.

```text
CONTEXT_BRIEF:
  One short paragraph summarizing what the scout learned.

LIKELY_RTL_AREA:
  Paths or module names likely involved.

SPEC_CHECKED:
  Files or event fields read.

REPO_FILES_CHECKED:
  Paths inspected, with short evidence snippets.

TOOLCHAIN_CHECKED:
  Commands, scripts, CI files, or docs inspected.

MODEL_ROUTE:
  Recommended model/profile and reason.

MISSING_INFO:
  Questions or blockers.

CONFIDENCE:
  high | medium | low | NEEDS_HUMAN

RECOMMENDED_NEXT_STEP:
  What the parent orchestrator should do next.
```

