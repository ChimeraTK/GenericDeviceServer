#!/usr/bin/python3
import mtca4u
import time
import sys
import os
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.exporters
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


def adc_dac_test(configuration):

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

    # Write DAC Tables to start using the DAC + VM on the DWC8VM1

    # Construct table values for I and Q for DAC
    amplitude = 15000

    dac_i = np.zeros(1024)
    dac_q = np.zeros(1024)

    # Make a pulse for in-phase component only
    # Since tables are strobed with 1.25 MHz, 1000 entries should give
    # about 800 microseconds long pulse
    dac_i[:1000] = amplitude

    device.update_dac_table(dac_i=dac_i, dac_q=dac_q)

    # Give time for DDR contents to change
    time.sleep(2)

    inst = DynamicPlotter(device=device)
    inst.run()


class DynamicPlotter:
    def __init__(self, device):

        self.app = QtGui.QApplication([])
        self.view1 = pg.GraphicsView()
        self.l1 = pg.GraphicsLayout(border=(100, 100, 100))
        self.view1.setCentralItem(self.l1)
        self.view1.show()
        self.view1.setWindowTitle("RAW ADC Signals")
        self.view1.resize(1700, 700)
        self.l1.nextRow()
        self.p_raw = []
        self.curve_list = []
        self.device = device
        self.daq_x_axis = np.linspace(
            0,
            self.device.dma_length / (self.device.app_clk_freq / 100),
            num=self.device.dma_length,
        )

        # Get the sequenced data from the deviceaccess and plot

        # WARNING:
        # The Channel 6 is internally blocked from outside signals (it shows Reference input instead)
        # The Channel 7 is internally blocked from outside signals (it shows VectorModulator Output instead)
        # This is a assembly option on the RTM. Please make sure your system is configured like this.
        # This script assumes that these internal loopbacks are present on the RTM boards. Hence we name
        # plots accordingly.
        for i in range(8):
            if i == 6:
                self.p_raw.append(
                    self.l1.addPlot(title="Reference Input Monitor".format(i))
                )
            elif i == 7:
                self.p_raw.append(
                    self.l1.addPlot(title="Vector Modulator Output Monitor".format(i))
                )
            else:
                self.p_raw.append(self.l1.addPlot(title="Channel {}".format(i)))
            self.p_raw[i].setLabel("bottom", "Time", units="s")
            self.curve_list.append(self.p_raw[i].plot())
            if i == 3:
                self.l1.nextRow()

        # QTimer
        self.timer = QtCore.QTimer()  # TODO: This should come from PCIe IRQ
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(1000)

    def updateplot(self):
        daq0_data = self.device.read_daq()
        for i in range(8):
            self.curve_list[i].setData(
                self.daq_x_axis, daq0_data[i, : self.device.dma_length]
            )

    def run(self):
        self.app.exec_()
