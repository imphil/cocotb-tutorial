# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Don't display deprecation warnings for this demo, they distract from the
# content.
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import to use PyVSC.
import vsc

# Imports to use cocotb.
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly

log = cocotb.logging.getLogger("cocotb.test")

@vsc.randobj
class RamRequest:
    """ A randomized RAM request. """
    def __init__(self):
        self.addr = vsc.rand_uint8_t()
        self.write_data = vsc.rand_uint32_t()
        self.write_enable = vsc.rand_bit_t()

    def __str__(self):
        if self.write_enable:
            return f"Write {self.write_data:#x} to address {self.addr:#02x}"
        else:
            return f"Read from address {self.addr:#02x}"

    @vsc.constraint
    def addr_c(self):
        # Constraint: addresses must be below 100
        self.addr < 100

    @vsc.dynamic_constraint
    def write_only(self):
        """ Write requests only. """
        self.write_enable == 1

@vsc.covergroup
class RamTransactionCovergroup:
    def __init__(self, ram_req):
        self.addr_cp = vsc.coverpoint(ram_req.addr)
        self.type_cp = vsc.coverpoint(ram_req.write_enable)

@cocotb.test()
async def test_ram(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, units='ns').start())
    dut.rst_ni.value = 1

    req = RamRequest()

    ram_transaction_cg = RamTransactionCovergroup(req)

    for _ in range(100):
        # Create a random request.
        req.randomize()

        # Randomize, but generate only write requests.
        #with req.randomize_with() as it:
        #    it.write_only()

        # Let's print the request on the console to see what's going on.
        dut._log.info(f"Request: {req}")

        # Drive the DUT with this request.
        await RisingEdge(dut.clk_i)
        dut.addr_i.value = req.addr
        dut.data_i.value = req.write_data
        dut.write_enable_i.value = req.write_enable

        await ReadOnly()
        ram_transaction_cg.sample()

    await ClockCycles(dut.clk_i, 2)

    # Print out coverage report to console.
    dut._log.info("Coverage Report: \n" + vsc.get_coverage_report())
