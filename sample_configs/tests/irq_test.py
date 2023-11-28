#!/usr/bin/python3
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

# File/Plots naming scheme
plot_extension = ".png"
raw_plot_file_name = "raw_adc_plot" + plot_extension

# Fetch the logger
logger = logging.getLogger(__name__)


def irq_test(configuration):

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

    # Enable the first IRQ channel. Example Design only uses the first 
    # channel. Using other PCIe IRQ will not work.
    device.enable_irq(enable=1, channel=0)

    while True:
        start = time.time()
        device.wait_irq()
        end = time.time()
        duration = end - start
        freq = 1 / duration
        print(
            "Time between IRQ: "
            + f"{duration:3.6f}"
            + " seconds.\tIRQ Arrival Frequency (Hz): "
            + f"{freq:3.6f}"
            + "\n",
            end="\r",
            flush=True,
        )
