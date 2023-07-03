#!/usr/bin/python3
import mtca4u
import time
import sys
import os
import numpy as np
import logging
from datetime import datetime
import logging

dut_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dut"))
conf_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../configurations")
)
sys.path.append(dut_path)
sys.path.append(conf_path)

from dut.dut import dut
from configurations import *

# Fetch the logger
logger = logging.getLogger(__name__)

def initialize(configuration):

    logger.info("Selected Configuration Properties: ")
    logger.info(str(configurations[configuration]))

    device = dut(
        dmap_location="./include/temp.dmap",
        device_name="device_reg",
        app_clk_freq=configurations[configuration]["app_clk_freq"],
        trigger_rate=configurations[configuration]["trigger_rate"],
        rtm_name=configurations[configuration]["rtm_name"],
        dma_length=configurations[configuration]["dma_length"],
        ad9510_input=configurations[configuration]["ad9510_input"],
        ad9510_division=configurations[configuration]["ad9510_division"],
        pll_config=configurations[configuration]["pll_config"],
    )

    # Initialize the board
    device.initialize_board()