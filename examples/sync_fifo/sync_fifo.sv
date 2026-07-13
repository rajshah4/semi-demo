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
  logic [ADDR_WIDTH:0] wr_ptr;
  logic [ADDR_WIDTH:0] rd_ptr;
  logic [ADDR_WIDTH:0] count;

  wire wr_valid = wr_en && !full;
  wire rd_valid = rd_en && !empty;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
    end else begin
      if (wr_valid && !rd_valid) begin
        wr_ptr <= (wr_ptr == DEPTH - 1) ? '0 : wr_ptr + 1;
        count <= count + 1;
      end else if (!wr_valid && rd_valid) begin
        rd_ptr <= (rd_ptr == DEPTH - 1) ? '0 : rd_ptr + 1;
        count <= count - 1;
      end else if (wr_valid && rd_valid) begin
        wr_ptr <= (wr_ptr == DEPTH - 1) ? '0 : wr_ptr + 1;
        rd_ptr <= (rd_ptr == DEPTH - 1) ? '0 : rd_ptr + 1;
      end
    end
  end

  always_ff @(posedge clk) begin
    if (wr_valid) begin
      mem[wr_ptr[ADDR_WIDTH-1:0]] <= din;
    end
  end

  assign dout = mem[rd_ptr[ADDR_WIDTH-1:0]];
  assign full = (count == DEPTH);
  assign empty = (count == 0);

endmodule
