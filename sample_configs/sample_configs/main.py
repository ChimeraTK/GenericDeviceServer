#!/usr/bin/env python3
import argparse
import os
import sys
import logging
import pathlib
from datetime import datetime

test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./tests"))
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./include"))

sys.path.append(test_path)
sys.path.append(include_path)

from xdma_wrapper import xdma_wrapper

from create_dmap import create_dmap

# Initiate the logger
log_file_name = "test_sequence.log"

stdout_handler = logging.StreamHandler(sys.stdout)


logging.basicConfig(level=logging.DEBUG)

# Initiate the parser

print(
    " ---------------------------------------------------------------------- \n"
    " --          ____  _____________  __                                 -- \n"
    " --         / __ \/ ____/ ___/\ \/ /         _   _   _               -- \n"
    " --        / / / / __/  \__ \  \  /         / \ / \ / \              -- \n"
    " --       / /_/ / /___ ___/ /  / /       = ( M | S | K )=            -- \n"
    " --      /_____/_____//____/  /_/           \_/ \_/ \_/              -- \n"
    " --                                                                  -- \n"
    " ---------------------------------------------------------------------- \n"
    " --! @copyright Copyright 2021 DESY                                     \n"
    " --! the Apache License, Version 2.0                                    \n"
    " ---------------------------------------------------------------------- \n"
)

welcome_text = " Welcome to the SIS8300KU Example Application"
parser = argparse.ArgumentParser(description=welcome_text)

parser.add_argument(
    "-v", "--version", help="shows program version", action="store_true"
)
parser.add_argument("-t", "--test", help="test method", required=True)
parser.add_argument(
    "-rm", "--regmap", help="register map file pointer", default="example"
)
parser.add_argument("-s", "--slot", help="MTCA slot number", type=int, required=True)
parser.add_argument("-c", "--conf", help="configuratio/project name", required=True)

# Read arguments from the command line
args = parser.parse_args()

# Check if user wants to use 'default' register map file
if args.regmap == "example":
    if args.conf == "ds8vm1":
        args.regmap = "example_ds8vm1.mapp"
    elif args.conf == "dwc8vm1" or args.conf == "dwc8vm1_w_rtm_clk":
        args.regmap = "example_dwc8vm1.mapp"
    else:
        print("Unknown configuration selected! Choose either ds8vm1, dwc8vm1 or dwc8vm1_w_rtm_clk")
        sys.exit(1)

# Create temperoray dmap file
logging.info("Producing temporary dmap file")
create_dmap(
    reg_map_file=args.regmap, slot=args.slot, dummy_mode=False
)

if args.test == "adc_dac_test":
    logging.info("Initializing the FPGA and performing ADC and DAC test...\n")
    from adc_dac_test import adc_dac_test
    adc_dac_test(configuration=args.conf)
elif args.test == "initialize":
    logging.info("Initializing the FPGA...\n")
    from initialize import initialize
    initialize(configuration=args.conf)
elif args.test == "irq_test":
    logging.info("Performing PCIe Interrupt(IRQ) test:\n")
    from irq_test import irq_test
    xdma_wrapper_device = xdma_wrapper(slot_number=args.slot)
    irq_test(configuration=args.conf, xdma_wrapper_inst=xdma_wrapper_device)
else:
    print("Unknown test sequence")
    sys.exit(1)

logging.info("Test Sequence: Completed!")

sys.exit()
