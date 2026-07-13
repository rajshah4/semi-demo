`timescale 1ns/1ps

module sync_fifo_tb;
  localparam int WIDTH = 8;
  localparam int DEPTH = 16;

  logic clk;
  logic rst_n;
  logic wr_en;
  logic rd_en;
  logic [WIDTH-1:0] din;
  logic [WIDTH-1:0] dout;
  logic full;
  logic empty;

  sync_fifo #(
    .WIDTH(WIDTH),
    .DEPTH(DEPTH)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .wr_en(wr_en),
    .rd_en(rd_en),
    .din(din),
    .dout(dout),
    .full(full),
    .empty(empty)
  );

  initial clk = 1'b0;
  always #5 clk = ~clk;

  task automatic tick;
    begin
      @(posedge clk);
      #1;
    end
  endtask

  task automatic expect_flag(input bit value, input bit expected, input string name);
    begin
      if (value !== expected) begin
        $fatal(1, "%s expected %0b, got %0b", name, expected, value);
      end
    end
  endtask

  task automatic expect_data(input logic [WIDTH-1:0] value, input logic [WIDTH-1:0] expected);
    begin
      if (value !== expected) begin
        $fatal(1, "dout expected 0x%0h, got 0x%0h", expected, value);
      end
    end
  endtask

  integer i;

  initial begin
    rst_n = 1'b0;
    wr_en = 1'b0;
    rd_en = 1'b0;
    din = '0;

    repeat (3) tick();
    rst_n = 1'b1;
    tick();

    expect_flag(empty, 1'b1, "empty after reset");
    expect_flag(full, 1'b0, "full after reset");

    for (i = 0; i < DEPTH; i = i + 1) begin
      din = i[WIDTH-1:0];
      wr_en = 1'b1;
      rd_en = 1'b0;
      tick();
    end

    wr_en = 1'b0;
    expect_flag(full, 1'b1, "full after DEPTH writes");
    expect_flag(empty, 1'b0, "empty after DEPTH writes");

    for (i = 0; i < DEPTH; i = i + 1) begin
      rd_en = 1'b1;
      wr_en = 1'b0;
      tick();
      expect_data(dout, i[WIDTH-1:0]);
    end

    rd_en = 1'b0;
    tick();
    expect_flag(empty, 1'b1, "empty after DEPTH reads");
    expect_flag(full, 1'b0, "full after DEPTH reads");

    din = 8'hA1;
    wr_en = 1'b1;
    tick();
    din = 8'hB2;
    tick();

    din = 8'hC3;
    rd_en = 1'b1;
    wr_en = 1'b1;
    tick();
    expect_data(dout, 8'hA1);

    wr_en = 1'b0;
    rd_en = 1'b1;
    tick();
    expect_data(dout, 8'hB2);

    tick();
    expect_data(dout, 8'hC3);

    rd_en = 1'b0;
    tick();
    expect_flag(empty, 1'b1, "empty after simultaneous read/write sequence");

    $display("SYNC_FIFO_TB_PASS");
    $finish;
  end
endmodule
