---
name: foundry-eda-validation
description: Use for deterministic validation of foundry RTL changes with static checks and optional EDA tools such as Verilator, Icarus Verilog, and Yosys.
---

# Foundry EDA Validation

## Core Rule

EDA tools and deterministic checks are the correctness authority. Model output
is useful for generation and summarization, but RTL changes are not complete
until validation evidence is captured.

## Skill-Owned Scripts

- `scripts/validate_rtl.sh`: validates `rtl/sync_fifo.sv` and
  `tb/sync_fifo_tb.sv` by default, then runs Verilator, Icarus Verilog, and
  Yosys when those tools are installed.

Run it from the repository root:

```bash
bash skills/foundry-eda-validation/scripts/validate_rtl.sh
```

For explicit files:

```bash
bash skills/foundry-eda-validation/scripts/validate_rtl.sh rtl/sync_fifo.sv tb/sync_fifo_tb.sv
```

## Reporting

Always report:

- the exact command
- which checks passed or failed
- whether full EDA tools ran or the result was static-only
- any missing toolchain dependency
- the next human review decision
