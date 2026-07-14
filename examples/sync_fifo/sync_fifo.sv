// Synchronous FIFO with parameterized width and depth
// Generated with ChipCraftX specialist routing and agent refinement

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

  // Memory storage
  logic [WIDTH-1:0] mem [0:DEPTH-1];
  
  // Read and write pointers
  logic [ADDR_WIDTH-1:0] wr_ptr;
  logic [ADDR_WIDTH-1:0] rd_ptr;
  
  // Occupancy count for accurate full/empty flag generation
  logic [ADDR_WIDTH:0] count;

  // Full and empty flag generation
  assign full = (count == DEPTH);
  assign empty = (count == 0);

  // Write operation: write when enabled and not full
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
    end else if (wr_en && !full) begin
      mem[wr_ptr] <= din;
      wr_ptr <= (wr_ptr + 1) % DEPTH;
    end
  end

  // Read operation: advance read pointer when enabled and not empty
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      rd_ptr <= '0;
    end else if (rd_en && !empty) begin
      rd_ptr <= (rd_ptr + 1) % DEPTH;
    end
  end

  // Output data register
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      dout <= '0;
    end else if (rd_en && !empty) begin
      dout <= mem[rd_ptr];
    end
  end

  // Occupancy count: tracks number of valid entries
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      count <= '0;
    end else begin
      case ({wr_en && !full, rd_en && !empty})
        2'b10: count <= count + 1;  // Write only
        2'b01: count <= count - 1;  // Read only
        default: count <= count;     // Both or neither
      endcase
    end
  end

endmodule
