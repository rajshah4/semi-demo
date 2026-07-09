# Toolchain Image

## Why Pre-Bake Tools

EDA tools and semiconductor workflows often have heavy setup, brittle dependencies, and licensing or PDK requirements. A pre-baked image turns the agent runtime into a repeatable engineering workstation.

## Good First Tools

- Verilator: RTL lint and simulation
- Icarus Verilog: simple Verilog simulation
- Yosys: synthesis checks
- Verible: Verilog/SystemVerilog formatting and linting
- cocotb: Python testbenches

## Heavier Enterprise Tools

- Slang or Surelog/UHDM for SystemVerilog parsing/elaboration
- OpenROAD/OpenLane for digital implementation flows
- SkyWater 130 or GF180 PDKs for open PDK demos
- internal foundry scripts and templates
- license config and approved EDA paths

## Demo Guidance

Do not start with the heaviest toolchain unless it is already reliable. Start with Verilator or Icarus plus a small testbench. Then explain that the same workflow can run inside a larger approved image.

## Recommended Demo Image

First image:

- start from `ghcr.io/openhands/agent-server:<approved-python-tag>`
- install `verilator`, `iverilog`, `yosys`, `verible`, `gtkwave`, `make`, `jq`, and `ripgrep`
- keep the inherited OpenHands entrypoint
- add a marker file such as `/etc/openhands-semi-eda-image`
- add `semi-demo` validation helpers, but do not bake secrets into the image

Verification command inside a fresh conversation:

```bash
which verilator iverilog yosys
bash scripts/validate_rtl.sh rtl/sync_fifo.sv tb/sync_fifo_tb.sv
```

The local custom-image examples currently live under:

```text
/Users/rajiv.shah/Code/install_replicate/openhands-custom-image
/Users/rajiv.shah/Code/install_replicate/custom-image-smoke-test
```

Use the smoke-test image first to prove Replicated is honoring the custom sandbox image setting, then publish the EDA image.

## Bigger Image Later

After the lightweight EDA image is stable, add heavier flows only if the meeting needs them:

- Slang or Surelog/UHDM for deeper SystemVerilog elaboration
- OpenROAD/OpenLane for place-and-route stories
- SkyWater 130 or GF180 PDK assets for open PDK demos
- internal foundry lint waivers, design templates, and license config

This keeps the first demo reliable while preserving the enterprise story: foundry IT can bake large, approved toolchains into the runtime.

## Image Story

> The model is only one part of the demo. The real enterprise value is an approved runtime image with models, EDA tools, PDKs, scripts, secrets, and policies already wired together.
