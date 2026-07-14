// Synthesizable SystemVerilog synchronous FIFO
// Parameters: WIDTH (data width), DEPTH (FIFO depth)
// Ports: clk, rst_n (active-low reset), wr_en, rd_en, din, dout, full, empty
// Supports simultaneous read/write when neither operation violates full/empty

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
      case ({wr_en && !full, rd_en && !empty})
        2'b10: begin
          mem[wr_ptr] <= din;
          wr_ptr <= (wr_ptr == DEPTH-1) ? '0 : wr_ptr + 1'b1;
          count <= count + 1'b1;
        end
        2'b01: begin
          dout <= mem[rd_ptr];
          rd_ptr <= (rd_ptr == DEPTH-1) ? '0 : rd_ptr + 1'b1;
          count <= count - 1'b1;
        end
        2'b11: begin
          mem[wr_ptr] <= din;
          wr_ptr <= (wr_ptr == DEPTH-1) ? '0 : wr_ptr + 1'b1;
          dout <= mem[rd_ptr];
          rd_ptr <= (rd_ptr == DEPTH-1) ? '0 : rd_ptr + 1'b1;
        end
        default: ;
      endcase
    end
  end

endmodule
