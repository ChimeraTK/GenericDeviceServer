#!/usr/bin/python3
import deviceaccess as da
import time
import sys
import datetime
import numpy as np
import logging

pll_config_location = "./include/ds8vm1_pll_config_files/"

# Fetch the logger
logger = logging.getLogger(__name__)


class dut:
    def __init__(
        self,
        dmap_location,
        device_name,
        app_clk_freq,
        trigger_rate,
        rtm_name,
        dma_length,
        ad9510_input,
        ad9510_division,
        pll_config,
    ):

        self.app_clk_freq = app_clk_freq
        self.trigger_rate = trigger_rate
        self.rtm_name = rtm_name
        self.dma_length = dma_length
        self.ad9510_input = ad9510_input
        self.pll_config = pll_config
        self.ad9510_division = ad9510_division

        # Creating device entry
        da.setDMapFilePath(dmap_location)
        self.device = da.Device(device_name)
        self.device.open()
        
        # Must for Push type Accessor
        self.device.activateAsyncRead()

        # Create accessor for IRQ 
        self.irqAcc = self.device.getOneDRegisterAccessor(np.int32, "/IRQ", 0, 0, [da.AccessMode.wait_for_new_data])


    def initialize_board(self):
        logger.info("Board is not initialized.. Doing the init script")

        # Selecting internally generated application clock while
        # we configure things...
        self.device.write("BSP.CLK_SEL", 0)

        self.device.write("BSP.RESET_N", 0)
        time.sleep(0.01)
        self.device.write("BSP.RESET_N", 1)
        time.sleep(0.01)

        # RTM Specific Configuration
        if self.rtm_name == "RTM_DWC8VM1":
            logger.info("Selected RTM Type: DWC8VM1")

            # allow drive in RF switch (Care for polarity)
            # When CON_RTM_INTERLOCK_NEGATE = 0 => WORD_INTERLOCK = 1 means drive is permitted
            self.device.write("RTM.RF_PERMIT", 1)

            # program common mode DAC for VM
            self.device.write("RTM.DACAB", 870)
            # ADC Clock Phase Adjustment (RTM Dependent Value!)
            # There is a mux in front of dual ADCs that provide additional phase change
            # This is used when D MA region channel assignment is not correct.
            # Default value for WORD_ADC_REVERT_CLK on DWC8VM1 is 0x18
            if self.ad9510_input == 0:
                self.device.write("BSP.ADC_REVERT_CLK", 0x18)
            elif self.ad9510_input == 1:
                self.device.write("BSP.ADC_REVERT_CLK", 0x10)
            else:
                logger.error("ad9510_input variable can only be 0 or 1")
                sys.exit(1)

            time.sleep(0.01)

        elif self.rtm_name == "RTM_DS8VM1":
            logger.info("Selected RTM Type: DS8VM1")

            logger.info(
                "Starting with DS8VM1 PLL configuration: " + str(self.pll_config)
            )

            # Bypassing the reference divider on DS8VM1     0x0=> divide by 1
            #                                               0x1=> divide by 2
            #                                               0x2=> divide by 3
            #                                               0x3=> divide by 4
            self.device.write("RTM.REFERENCE_DIV", 0)

            # Selecting the SMA CLK for CLKin1
            self.device.write("RTM.PLL_OSC_SEL", 1)

            # 0 => SMA Ref goes to CLKin2 + CPout1 goes into OSCin  1 => SMA Ref goes directly into OSCin
            self.device.write("RTM.PLL_CLK_IN_SEL", 1)

            # Create empty array for PLL configuration data
            registers = []

            # Open the file that comes from CodeLoader
            try:
                pll_file = open(
                    pll_config_location + "pll_config_" + self.pll_config + ".txt"
                )
            except:
                logger.error(
                    "Cannot open RTM_DS8VM1 PLL configuration file: pll_config_"
                    + self.pll_config
                    + ".txt"
                )
                sys.exit(1)

            pll_data = pll_file.readlines()

            for line in pll_data:
                register_string = line.strip().split()  # get rid of OS dependency
                registers.append(int(register_string[-1], 16))  # Convert to int

            logger.info(
                "Sending configuration of the PLL on the DS8VM1. This could take awhile..."
            )
            for index in range(len(registers)):
                while True:
                    if not self.device.read(
                        "RTM.PLL_BUSY"
                    ):  # Make sure PLL is not busy before we send a new command
                        self.device.write("RTM.PLL_DATA", registers[index])
                        break

            # program common mode DAC for VM (some f*cking magic number)
            self.device.write(
                "RTM.DAC_VM_COM_MODE_Q", 13600
            )  # Common Mode for VM for Q
            self.device.write(
                "RTM.DAC_VM_COM_MODE_I", 13600
            )  # Common Mode for VM for I

            # allow drive in RF switch (Care for polarity)
            # When CON_RTM_INTERLOCK_NEGATE = 0 => WORD_INTERLOCK = 1 means drive is permitted
            self.device.write("RTM.RF_PERMIT", 1)

            # ADC Clock Phase Adjustment (RTM Dependent Value!)
            # There is a mux in front of dual ADCs that provide additional phase change
            # This is used when DMA region channel assignment is not correct.
            # Default value for WORD_ADC_REVERT_CLK on RTM_DS8VM1 is 0x00
            self.device.write("BSP.ADC_REVERT_CLK", 0)
            time.sleep(0.01)

            logger.info(
                "RTM_DS8VM1 Configuration is done. Continuing the AMC configuration... "
            )

        else:
            logger.error("\n*****************************************************")
            logger.error("  Unknown RTM type entry.")
            logger.error("*****************************************************")
            sys.exit(1)

        # Set FUNCTION pin of the AD9510 as RESETB so we can hard-reset the AD9510
        # AD9510 0x58 register [6 downto 5] determines the FUNCTION pin
        self.device.write("BSP.AREA_SPI_DIV", 0x00, 0x58)
        time.sleep(0.01)
        # Update the registers of AD9510
        self.device.write("BSP.AREA_SPI_DIV", 0x01, 0x5A)
        time.sleep(0.01)

        # Reseting the PLL of the Struck using FUNCTION pin
        self.device.write("BSP.CLK_RST", 1)
        time.sleep(0.01)
        self.device.write("BSP.CLK_RST", 0)
        time.sleep(0.01)

        # Programming the Muxes of the Struck
        # We are configuring the muxes so that AD9510 PLL gets Quartz signal as CLK1
        muxData = [3, 3, 0, 0, 0, 0]
        self.device.write("BSP.CLK_MUX", muxData)
        time.sleep(0.01)

        # Selecting which CLK input will be used to distribute
        # 0 -> PLL uses clock coming from RTM(CLK2)    1 -> PLL uses clock coming from Muxes(CLK1)
        self.device.write("BSP.AREA_SPI_DIV", self.ad9510_input, 0x45)
        time.sleep(0.01)

        # PLL Power Down Mode is set to: Synchronous Power Down, PreScaler Mode -> Divider Value set to 1
        self.device.write("BSP.AREA_SPI_DIV", 0x43, 0x0A)
        time.sleep(0.01)

        # All Outputs levels  (LVPECL) are set to 660mV
        self.device.write("BSP.AREA_SPI_DIV", 0x0C, 0x3C)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", 0x0C, 0x3D)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", 0x0C, 0x3E)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", 0x0C, 0x3F)
        time.sleep(0.01)

        # Output Current Level = 3.5mA Termination 100ohms Output Type = LVDS
        self.device.write("BSP.AREA_SPI_DIV", 2, 0x40)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", 2, 0x41)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", 2, 0x42)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", 2, 0x43)
        time.sleep(0.01)

        # See AD9510 datasheet for more info on the registers 0x49 to 0x57
        if self.ad9510_division == 1:
            div_reg_val = 0x80
        elif self.ad9510_division == 2:
            div_reg_val = 0x00
        elif self.ad9510_division == 3:
            div_reg_val = 0x01
        elif self.ad9510_division == 4:
            div_reg_val = 0x11
        else:
            print("AD9510 division can only be 1-4")
            sys.exit(1)

        # Bypass and power down divider logic; route clock directly to output
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x49)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x4B)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x4D)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x4F)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x51)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x53)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x55)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_DIV", div_reg_val, 0x57)
        time.sleep(0.01)

        # Set FUNCTION pin of the AD9510 as SYNCB so we can align clock phases
        # AD9510 0x58 register [6 downto 5] determines the FUNCTION pin
        self.device.write("BSP.AREA_SPI_DIV", 0x20, 0x58)
        time.sleep(0.01)

        # Writing a 1 to this bit updates all registers and transfers all serial control port register buffer contents to
        # the control registers on the next rising SCLK edge
        self.device.write("BSP.AREA_SPI_DIV", 1, 0x5A)
        time.sleep(0.2)

        # Synchronizing the PLL of the Struck using FUNCTION pin
        self.device.write("BSP.CLK_RST", 1)
        time.sleep(0.01)
        self.device.write("BSP.CLK_RST", 0)
        time.sleep(0.01)

        # Check clock frequency (with timeout-like wait)
        clockOk = False
        logger.info("Wait for clock frequency readout")
        for i in range(0, 100):  # 10 seconds timeout
            time.sleep(0.1)
            if i % 10 == 0:
                # print('.', end='', flush=True)
                clockFrequency = self.device.read("BSP.CLK_FREQ", np.int32, 1)
            if abs(clockFrequency[0] - self.app_clk_freq) < 500000:
                logger.info(
                    "\nCorrect clock frequency detected: "
                    + str(clockFrequency[0] / 1000000)
                    + " MHz"
                )
                clockOk = True
                break

        if not clockOk:
            logger.error("\n*****************************************************")
            logger.error(
                "  Wrong clock frequency detected: "
                + str(clockFrequency[0] / 1000000)
                + " MHz"
            )
            logger.error("*****************************************************")
            ##sys.exit(1)

        logger.info("Continuing with the configuration...")

        # Selecting external clock for application part of the firmware
        self.device.write("BSP.CLK_SEL", 1)
        time.sleep(0.01)

        # Reset once again for ADC phase to match
        self.device.write("BSP.RESET_N", 0)
        time.sleep(0.01)
        self.device.write("BSP.RESET_N", 1)
        time.sleep(0.01)

        # program ADCs via SPI
        self.device.write("BSP.AREA_SPI_ADC", 0x3C, 0x00)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_ADC", 0x41, 0x14)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_ADC", 0x00, 0x0D)
        time.sleep(0.01)
        self.device.write("BSP.AREA_SPI_ADC", 0x01, 0xFF)
        time.sleep(0.01)

        # reset ADCs after programming clocks
        self.device.write("BSP.ADC_ENA", 0)
        time.sleep(0.01)
        self.device.write("BSP.ADC_ENA", 1)
        time.sleep(0.01)

        # Enable DAC
        self.device.write("BSP.DAC_ENA", 1)

        # Configure the trigger distribution
        # Example Design TIMING module channels:
        # Channel 0: DAQ Trigger
        # Channel 1: DAC DPM Table strobing

        self.device.write(
            "TIMING.SOURCE_SEL", 0, 0
        )  # DAQ trigger will be sourced from application clock

        self.device.write(
            "TIMING.SOURCE_SEL", 0, 1
        )  # DPM DAC Table strobe will be sourced from application clock (125MHz)

        self.device.write(
            "TIMING.SOURCE_SEL", 10, 2
        )  # Interrupt output will be same as DAQ trigger (This interrupt goes to xDMA EndPoint)

        self.device.write(
            "TIMING.SOURCE_SEL", 10, 3
        )  # Table trigger will be same as DAQ trigger

        self.device.write(
            "TIMING.SYNC_SEL", 1, 1
        )  # DPM DAC Table strobe will be synced with DAQ Trigger

        # Set DAQ trigger freq to 10 Hz by dividing it
        self.device.write("TIMING.DIVIDER_VALUE", self.app_clk_freq / 10 - 1, 0)

        # Set DAC Table Strobe to 1.25 MHz
        self.device.write("TIMING.DIVIDER_VALUE", 99, 1)

        self.device.write(
            "TIMING.ENABLE", 15
        )  # Enable all outputs from the TIMING module

        # Make sure DPM Memory pointer goes to 0 when table trigger comes
        # This makes tables output align with DAQ reading
        self.device.write("APP.DPM_MODE", 1)

        # Drive MLVDS Lanes 19Tx and 20Rx to High to enable Vector Modulator output
        self.device.write("APP.MLVDS_OE", 0x60)  # Output Enable
        self.device.write("APP.MLVDS_O", 0x60)  # Output Value

        # DAQ Configuration
        self.device.write("DAQ.SAMPLES", self.dma_length, 0)
        self.device.write("DAQ.STROBE_DIV", 99, 0)

        self.device.write("DAQ.TAB_SEL", 0, 0)  # Choose raw adc signals on mux
        self.device.write(
            "DAQ.DOUBLE_BUF_ENA", 1, 0
        )  # Enable double buffering for Region 0
        self.device.write("DAQ.ENABLE", 1, 0)  # Enable DAQ1 for now.

        self.set_attenuator(255, 63)  # All channels get 0dB attenuation at start

        compilation_unix_time = self.device.read("BSP.PRJ_TIMESTAMP")
        compilation_message = (
            "This firmware was compiled on:",
            datetime.datetime.fromtimestamp(int(compilation_unix_time)).strftime(
                "%d-%B-%Y %H:%M:%S"
            ),
        )
        logger.info(str(compilation_message))

        logger.info("Initialisation complete.")

    def read_daq(self):
        self.device.write(
            "DAQ.DOUBLE_BUF_ENA", 0, 0
        )  # Temporarily Disable Double Buffering

        time.sleep(0.1)  # Give time for last register to be written

        buf_to_read = int(not (self.device.read("DAQ.ACTIVE_BUF", np.int32, 0)))
        daq0_data = self.device.getTwoDRegisterAccessor(
            np.float32, "DAQBUF/DAQ_CTRL_BUF0", 0, 0
        )

        daq0_data.read()
        # daq0_data = self.device.read_sequences(
        #     "DAQBUF", "DAQ_CTRL_BUF{}".format(buf_to_read)
        # )

        self.device.write(
            "DAQ.DOUBLE_BUF_ENA", 1, 0
        )  # Enable the Double buffering again

        return daq0_data

    def update_dac_table(self, dac_i, dac_q):
        """Writes to the Tables for I and Q values going to DAC

        :param dac_i: In-phase component of DAC
        :type dac_i: numpy list 1024 width
        :param dac_q: Quadrature component of DAC
        :type dac_q: numpy list 1024 width
        """
        for i in range(1024):
            self.device.write("APP.AREA_DAC_I", dac_i[i], i)
            self.device.write("APP.AREA_DAC_Q", dac_q[i], i)

    def enable_irq(self, enable, channel):
        """Enables the particular PCIe IRQ channel

        :param enable: 1 -> Enable, 0 -> Disable
        :type enable: int
        :param channel: Choose which xDMA IRQ channel to enable/disable
        """
        self.device.write("BSP.PCIE_IRQ_ENA", enable, channel)

    def wait_irq(self):
        """Waits for the particular PCIe IRQ channel
        :param channel: Choose which xDMA IRQ channel to wait
        """
        self.irqAcc.read()

    def print_version(self):
        module_list = ["BSP.APP.DAQ.TIMING"]

        module_version = []
        for i in module_list:
            module_version.append(
                self.parse_version(int(self.device.read(i, "VERSION")))
            )

        for idx, val in enumerate(module_version):
            logger.info("{} Version numbers".format(module_list[idx]))
            logger.info("Major:\t" + str(module_version[idx][3]))
            logger.info("Minor:\t" + str(module_version[idx][2]))
            logger.info("Patch:\t" + str(module_version[idx][1]))
            logger.info("Commit:\t" + str(module_version[idx][0]))

    def parse_version(self, version):
        commit = version & 0xFF
        patch = (version & 0xFF00) >> 8
        minor = (version & 0xFF0000) >> 16
        major = (version & 0xFF000000) >> 24

        return commit, patch, minor, major

    def get_fifo_status(self):
        return self.device.read("DAQ.FIFO_STATUS")

    def fifo_overflowing(self):
        fifo_status_1 = self.get_fifo_status()
        time.sleep(0.5)
        fifo_status_2 = self.get_fifo_status()
        if np.array_equal(fifo_status_1, fifo_status_2):
            return False
        else:
            return True

    def report_adc_overflowing(self):
        status = int(self.device.read("APP.STATUS"))
        bits = [(status >> bit) & 1 for bit in range(10, -1, -1)]
        for i in range(10):
            if bits[10 - i] == 1:
                logger.warning("Channel {} ADC is overflowing!".format(i))

    def set_attenuator(self, channel, value):

        self.device.write("RTM.ATT_SEL", channel)

        while True:
            if not self.device.read("RTM.ATT_STATUS"):
                logger.info("Attenuators are idle and ready for a new value.")
                self.device.write("RTM.ATT_VAL", value)
                break
            else:
                logger.info("Attenuators seem to be busy.")
