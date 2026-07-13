// Starter RTL for the OpenHands semiconductor work cell.
//
// This file is intentionally incomplete. The `openhands-rtl-build` automation
// should replace it with a synthesizable FIFO implementation, ideally after
// switching to the `HF-ChipCraftX-RTLGen-7B` specialist profile.

module sync_fifo #(
  parameter int WIDTH = 8,
  parameter int DEPTH = 16
) (
  input  logic             clk,
  input  logic             rst_n,
  input  logic             wr_en,
  input  logic             rd_en,
  input  logic [WIDTH-1:0] din,
  output logic [WIDTH-1:0] dout,
  output logic             full,
  output logic             empty
);

  // TODO: implement storage, pointers, occupancy count, and flag logic.
  assign dout = '0;
  assign full = 1'b0;
  assign empty = 1'b1;

endmodule
