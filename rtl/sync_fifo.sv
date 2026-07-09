// Synchronous FIFO implementation
// Generated for OpenHands semiconductor demo
// Specialist model: HF-ChipCraftX-RTLGen-7B (intended)

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

  logic write_op;
  logic read_op;

  always_comb begin
    write_op = wr_en && !full;
    read_op = rd_en && !empty;
    full = (count == DEPTH[ADDR_WIDTH:0]);
    empty = (count == '0);
  end

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
      dout <= '0;
    end else begin
      if (write_op) begin
        mem[wr_ptr] <= din;
        wr_ptr <= (wr_ptr + 1'b1) % DEPTH[ADDR_WIDTH-1:0];
      end

      if (read_op) begin
        dout <= mem[rd_ptr];
        rd_ptr <= (rd_ptr + 1'b1) % DEPTH[ADDR_WIDTH-1:0];
      end

      case ({write_op, read_op})
        2'b10: count <= count + 1'b1;
        2'b01: count <= count - 1'b1;
        default: count <= count;
      endcase
    end
  end

endmodule
