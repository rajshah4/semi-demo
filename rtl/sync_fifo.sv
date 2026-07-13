// Synchronous FIFO implementation for OpenHands semiconductor demo.
// Generated for issue KAN-80: Implement synchronous FIFO
//
// Reset behavior: Active-low synchronous reset clears all pointers and flags.
// Write: Data written on posedge clk when wr_en=1 and full=0.
// Read: Data output updates on posedge clk when rd_en=1 and empty=0.
// Simultaneous read/write supported when FIFO is neither empty nor full.

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

  logic [WIDTH-1:0] storage [0:DEPTH-1];
  logic [ADDR_WIDTH-1:0] wr_ptr;
  logic [ADDR_WIDTH-1:0] rd_ptr;
  logic [$clog2(DEPTH+1)-1:0] count;

  wire wr_valid = wr_en && !full;
  wire rd_valid = rd_en && !empty;

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count  <= '0;
      dout   <= '0;
    end else begin
      if (wr_valid) begin
        storage[wr_ptr] <= din;
        wr_ptr <= (wr_ptr + 1) % DEPTH;
      end

      if (rd_valid) begin
        dout <= storage[rd_ptr];
        rd_ptr <= (rd_ptr + 1) % DEPTH;
      end

      case ({wr_valid, rd_valid})
        2'b10: count <= count + 1;
        2'b01: count <= count - 1;
        default: count <= count;
      endcase
    end
  end

  assign empty = (count == 0);
  assign full  = (count == DEPTH);

endmodule
