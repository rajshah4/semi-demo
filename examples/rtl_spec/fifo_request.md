# RTL Request: Synchronous FIFO

Create a synthesizable SystemVerilog module named `sync_fifo`.

## Parameters

- `WIDTH = 8`
- `DEPTH = 16`

## Ports

- `input logic clk`
- `input logic rst_n`
- `input logic wr_en`
- `input logic rd_en`
- `input logic [WIDTH-1:0] din`
- `output logic [WIDTH-1:0] dout`
- `output logic full`
- `output logic empty`

## Behavior

- Active-low synchronous reset.
- Write `din` when `wr_en` is high and `full` is low.
- Read to `dout` when `rd_en` is high and `empty` is low.
- Support simultaneous read and write when neither operation violates full or empty.
- Maintain accurate `full` and `empty` flags.
- Avoid combinational loops.
- Produce synthesizable RTL.

## Validation

- Lint the generated RTL.
- Simulate reset, write until full, read until empty, and simultaneous read/write.
- Summarize any tool failures and patch until passing.

