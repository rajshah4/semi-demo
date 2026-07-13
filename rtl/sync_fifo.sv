// Synchronous FIFO implementation for OpenHands semiconductor demo.
// Generated for issue #17 - KAN-81
//
// Parameters:
//   WIDTH - Data width in bits (default: 8)
//   DEPTH - FIFO depth in entries (default: 16)
//
// Reset behavior:
//   Active-low synchronous reset clears read/write pointers and sets empty flag.
//
// Write behavior:
//   Write occurs when wr_en is high and full is low.
//   Data is captured on rising edge of clk.
//
// Read behavior:
//   Read occurs when rd_en is high and empty is low.
//   Data is available one cycle after rd_en assertion.
//
// Simultaneous read/write:
//   Supported when neither operation violates full or empty conditions.

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
  
  logic [WIDTH-1:0] mem [DEPTH-1:0];
  logic [ADDR_WIDTH-1:0] wr_ptr;
  logic [ADDR_WIDTH-1:0] rd_ptr;
  logic [ADDR_WIDTH:0] count;
  
  wire wr_valid = wr_en && !full;
  wire rd_valid = rd_en && !empty;
  
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
      dout <= '0;
    end else begin
      if (wr_valid) begin
        mem[wr_ptr] <= din;
        wr_ptr <= (wr_ptr == DEPTH-1) ? '0 : wr_ptr + 1'b1;
      end
      
      if (rd_valid) begin
        dout <= mem[rd_ptr];
        rd_ptr <= (rd_ptr == DEPTH-1) ? '0 : rd_ptr + 1'b1;
      end
      
      case ({wr_valid, rd_valid})
        2'b10: count <= count + 1'b1;
        2'b01: count <= count - 1'b1;
        default: count <= count;
      endcase
    end
  end
  
  assign full = (count == DEPTH);
  assign empty = (count == '0);

endmodule
