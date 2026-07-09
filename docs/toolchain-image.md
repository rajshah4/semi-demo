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

## Image Story

> The model is only one part of the demo. The real enterprise value is an approved runtime image with models, EDA tools, PDKs, scripts, secrets, and policies already wired together.

