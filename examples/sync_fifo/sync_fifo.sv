// Synthesizable synchronous FIFO for streaming adapter.
// Generated with assistance from ChipCraftX RTLGen-7B via HF Featherless AI.
// SHA256: 3aa3553b1e8fbdcebbee55ef2bd2406f312bf51e37deb801ed4fdc000f3ad0dd
//
// Parameterizable data width and FIFO depth. Uses synchronous active-low reset
// and a single clock. Supports write enable, read enable, full flag, and empty
// flag behavior. Simultaneous read/write supported when neither violates flags.

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

  localparam int PTR_WIDTH = $clog2(DEPTH);
  localparam int FULL_COUNT = DEPTH;
  localparam int EMPTY_COUNT = 0;

  logic [WIDTH-1:0] storage [0:DEPTH-1];
  logic [PTR_WIDTH-1:0] wr_ptr;
  logic [PTR_WIDTH-1:0] rd_ptr;
  logic [PTR_WIDTH:0] count;

  wire write_legal = wr_en && !full;
  wire read_legal = rd_en && !empty;

  always @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
    end else begin
      if (write_legal) begin
        storage[wr_ptr] <= din;
        wr_ptr <= wr_ptr + 1'b1;
      end
      if (read_legal) begin
        rd_ptr <= rd_ptr + 1'b1;
      end
      case ({write_legal, read_legal})
        2'b10: count <= count + 1'b1;
        2'b01: count <= count - 1'b1;
        default: count <= count;
      endcase
    end
  end

  assign full = (count == FULL_COUNT);
  assign empty = (count == EMPTY_COUNT);
  assign dout = storage[rd_ptr];

endmodule
