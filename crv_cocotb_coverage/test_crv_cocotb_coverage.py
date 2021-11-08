# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# Import to use cocotb-coverage.
from cocotb_coverage.coverage import coverage_db, CoverPoint
from cocotb_coverage import crv

# Imports to use cocotb.
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly

log = cocotb.logging.getLogger("cocotb.test")

class RamRequest(crv.Randomized):

    def __init__(self):
        crv.Randomized.__init__(self)

        self.addr = 0
        self.write_data = 0
        self.write_enable = 0

        self.add_rand("addr", list(range(0, 256)))
        # Note: A full 32 bit range leads to massive memory consumption!
        self.add_rand("write_data", list(range(0, 256)))
        self.add_rand("write_enable", [0, 1])

        # Addresses must be below 100.
        self.add_constraint(lambda addr: addr < 100)

    def __str__(self):
        if self.write_enable:
            return f"Write {self.write_data:#x} to address {self.addr:#02x}"
        else:
            return f"Read from address {self.addr:#02x}"


@CoverPoint(
    "top.addr_cp",
    xf = lambda ram_req: ram_req.addr,
    bins = list(range(0, 256)),
)
@CoverPoint(
    "top.type_cp",
    xf = lambda ram_req: "WRITE" if ram_req.write_enable else "READ",
    bins = ["WRITE", "READ"]
)
def sample(ram_req):
    pass

@cocotb.test()
async def test_ram(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, units='ns').start())
    dut.rst_ni.value = 1

    req = RamRequest()

    for _ in range(100):
        # Create a random request.
        req.randomize()

        # Randomize, but generate only write requests.
        #req.randomize_with(lambda write_enable: write_enable == True)

        # Let's print the request on the console to see what's going on.
        dut._log.info(f"Request: {req}")

        # Drive the DUT with this request.
        await RisingEdge(dut.clk_i)
        dut.addr_i.value = req.addr
        dut.data_i.value = req.write_data
        dut.write_enable_i.value = req.write_enable

        await ReadOnly()
        sample(req)

    await ClockCycles(dut.clk_i, 2)

    # Print out coverage report to console.
    coverage_db.report_coverage(dut._log.info)

    # Write a coverage.xml file.
    coverage_db.export_to_xml()
