// Synchronous FIFO with parameterizable width and depth
// Generated for foundry IP streaming adapter use case
// Active-low reset, single clock domain

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
  logic [ADDR_WIDTH:0] wr_ptr;
  logic [ADDR_WIDTH:0] rd_ptr;
  logic [ADDR_WIDTH:0] count;

  // Active-low synchronous reset behavior
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      wr_ptr <= '0;
      rd_ptr <= '0;
      count <= '0;
    end else begin
      case ({wr_en && !full, rd_en && !empty})
        2'b10: begin  // Write only
          mem[wr_ptr[ADDR_WIDTH-1:0]] <= din;
          wr_ptr <= wr_ptr + 1'b1;
          count <= count + 1'b1;
        end
        2'b01: begin  // Read only
          rd_ptr <= rd_ptr + 1'b1;
          count <= count - 1'b1;
        end
        2'b11: begin  // Simultaneous read and write
          mem[wr_ptr[ADDR_WIDTH-1:0]] <= din;
          wr_ptr <= wr_ptr + 1'b1;
          rd_ptr <= rd_ptr + 1'b1;
          // count remains unchanged
        end
        default: begin
          // No operation
        end
      endcase
    end
  end

  // Output data register for read operations
  always_ff @(posedge clk) begin
    if (!rst_n) begin
      dout <= '0;
    end else if (rd_en && !empty) begin
      dout <= mem[rd_ptr[ADDR_WIDTH-1:0]];
    end
  end

  // Full and empty flag generation
  assign full = (count == (ADDR_WIDTH+1)'(DEPTH));
  assign empty = (count == '0);

endmodule
