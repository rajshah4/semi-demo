// Synchronous FIFO for streaming adapter
// Generated for foundry IP work cell
// Parameters: WIDTH (data width), DEPTH (FIFO depth)
// Uses active-low synchronous reset, single clock domain

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

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
      dout <= '0;
    end else begin
      if (wr_en && !full) begin
        mem[wr_ptr] <= din;
        wr_ptr <= (wr_ptr + 1) % DEPTH;
      end

      if (rd_en && !empty) begin
        dout <= mem[rd_ptr];
        rd_ptr <= (rd_ptr + 1) % DEPTH;
      end

      case ({wr_en && !full, rd_en && !empty})
        2'b10: count <= count + 1;
        2'b01: count <= count - 1;
        default: count <= count;
      endcase
    end
  end

endmodule
