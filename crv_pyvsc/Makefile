# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

PWD=$(shell pwd)

VERILOG_SOURCES = $(PWD)/ram.sv

TOPLEVEL         = ram
TOPLEVEL_LANG    = verilog
MODULE           = test_crv_pyvsc

ifeq ($(SIM),verilator)
  SIM_ARGS=-Wno-error
  EXTRA_ARGS += --trace-fst --trace-structs

  ifeq ($(COVERAGE),1)
    EXTRA_ARGS += --coverage
  endif
else ifeq ($(SIM),riviera)
  EXTRA_ARGS += -licqueue
endif

include $(shell cocotb-config --makefiles)/Makefile.sim
