// Synchronous FIFO
// Synthesizable SystemVerilog implementation for streaming adapter
//
// Parameters:
//   WIDTH: Data width (default 8)
//   DEPTH: FIFO depth (default 16)
//
// Reset behavior:
//   Active-low synchronous reset clears pointers and sets empty flag
//
// Boundary behavior:
//   Write when wr_en=1 and full=0
//   Read when rd_en=1 and empty=0
//   Simultaneous read/write allowed when neither violates full/empty

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

  assign full = (count == DEPTH);
  assign empty = (count == 0);

  logic do_write;
  logic do_read;
  assign do_write = wr_en && !full;
  assign do_read = rd_en && !empty;

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
    end else begin
      if (do_write) begin
        mem[wr_ptr] <= din;
        wr_ptr <= (wr_ptr + 1) % DEPTH;
      end

      if (do_read) begin
        rd_ptr <= (rd_ptr + 1) % DEPTH;
      end

      case ({do_write, do_read})
        2'b10: count <= count + 1;
        2'b01: count <= count - 1;
        default: count <= count;
      endcase
    end
  end

  assign dout = mem[rd_ptr];

endmodule
