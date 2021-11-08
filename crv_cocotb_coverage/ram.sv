// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0

module ram (
  input logic clk_i,
  input logic rst_ni,

  input logic [7:0] addr_i,
  input logic [31:0] data_i,
  input logic write_enable_i,

  output logic [31:0] data_o
);

  logic [31:0] mem [256];

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      data_o <= 32'h0;
    end else begin
      if (write_enable_i) begin
        mem[addr_i] <= data_i;
      end else begin
        data_o <= mem[addr_i];
      end
    end
  end

endmodule
