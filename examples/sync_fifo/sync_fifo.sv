// Synchronous FIFO implementation
// Generated for OpenHands Foundry RTL workflow
//
// Module: sync_fifo
// Description: Parameterized synchronous FIFO with configurable width and depth
// Features:
//   - Active-low asynchronous reset
//   - Write enable with full flag protection
//   - Read enable with empty flag protection
//   - Simultaneous read/write support
//   - Wraparound pointer handling

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

  localparam int ADDR_WIDTH = $clog2(DEPTH);

  logic [WIDTH-1:0] mem [0:DEPTH-1];
  logic [ADDR_WIDTH-1:0] wr_ptr;
  logic [ADDR_WIDTH-1:0] rd_ptr;
  logic [ADDR_WIDTH:0] count;

  logic do_write;
  logic do_read;

  assign do_write = wr_en && !full;
  assign do_read = rd_en && !empty;

  assign full = (count == DEPTH);
  assign empty = (count == 0);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
      dout <= '0;
    end else begin
      if (do_write) begin
        mem[wr_ptr] <= din;
        if (wr_ptr == DEPTH - 1)
          wr_ptr <= '0;
        else
          wr_ptr <= wr_ptr + 1'b1;
      end

      if (do_read) begin
        dout <= mem[rd_ptr];
        if (rd_ptr == DEPTH - 1)
          rd_ptr <= '0;
        else
          rd_ptr <= rd_ptr + 1'b1;
      end

      case ({do_write, do_read})
        2'b10: count <= count + 1'b1;
        2'b01: count <= count - 1'b1;
        default: count <= count;
      endcase
    end
  end

endmodule
