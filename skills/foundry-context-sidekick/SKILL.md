---
name: foundry-context-sidekick
description: Read-only context scout for foundry RTL demo requests. Use before implementation when Codex/OpenHands needs to gather spec, repo, toolchain, and model-route context without editing code.
---

# Foundry Context Sidekick

## Hard Boundaries

- Read only.
- Do not edit files.
- Do not create branches, commits, PRs, labels, comments, or status changes.
- Do not read or print secrets, `.env` values, credentials, tokens, license files, or private keys.
- Prefer deterministic search before broad reasoning.
- Stop with `NEEDS_HUMAN` when the request cannot be mapped with at least medium confidence.

## Scout Roles

| Scout | Roots | Job | Budget |
|---|---|---|---|
| `spec-scout` | issue body, `examples/`, `docs/`, `openspec/` if present | Normalize requirements and acceptance tests | At most four matching files |
| `rtl-repo-scout` | RTL/source/test directories | Find likely modules, test patterns, and integration points | At most four matching files |
| `toolchain-scout` | repo scripts, CI, Makefiles, docs | Find available EDA commands and missing image dependencies | At most four matching files |
| `model-route-scout` | `configs/`, `docs/repo-memory/` | Recommend model route and data-boundary policy | At most four matching files |

## Output Contract

Return a compact brief with:

- `CONTEXT_BRIEF`
- `LIKELY_RTL_AREA`
- `SPEC_CHECKED`
- `REPO_FILES_CHECKED`
- `TOOLCHAIN_CHECKED`
- `MODEL_ROUTE`
- `MISSING_INFO`
- `CONFIDENCE`
- `RECOMMENDED_NEXT_STEP`

