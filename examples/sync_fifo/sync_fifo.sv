// Synchronous FIFO with parameterizable width and depth.
// Generated from ChipCraftX RTLGen-7B first draft, reviewed and completed by OpenHands orchestrator.
//
// Reset behavior: Active-low synchronous reset clears all pointers and count.
// Write: When wr_en is high and full is low, din is stored at wr_ptr.
// Read: When rd_en is high and empty is low, data at rd_ptr appears on dout.
// Simultaneous read/write: Supported when neither operation violates full or empty.

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

  logic [WIDTH-1:0] fifo_mem [0:DEPTH-1];
  logic [$clog2(DEPTH):0] count;
  logic [$clog2(DEPTH)-1:0] wr_ptr;
  logic [$clog2(DEPTH)-1:0] rd_ptr;

  assign full  = (count == DEPTH);
  assign empty = (count == 0);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count  <= '0;
    end else begin
      case ({wr_en && !full, rd_en && !empty})
        2'b10: begin
          fifo_mem[wr_ptr] <= din;
          wr_ptr <= wr_ptr + 1'b1;
          count  <= count + 1'b1;
        end
        2'b01: begin
          rd_ptr <= rd_ptr + 1'b1;
          count  <= count - 1'b1;
        end
        2'b11: begin
          fifo_mem[wr_ptr] <= din;
          wr_ptr <= wr_ptr + 1'b1;
          rd_ptr <= rd_ptr + 1'b1;
        end
        default: ;
      endcase
    end
  end

  assign dout = fifo_mem[rd_ptr];

endmodule
