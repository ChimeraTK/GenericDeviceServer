#! /usr/bin/python3

import mtca4u
import os

mtca4u.set_dmap_location("devices.dmap")
dev = mtca4u.Device("ADC_BOARD")

dev.write("BSP", "SCRATCH", 42)


fid = dev.read("BSP", "ID")
if fid != 0:
    # Forward to CG's script for real hw initialization
    err=os.system("./main.py -t initialize -s 3 -c dwc8vm1")
    exit(err!=0)
else:
    print ("initscript.py for dummy done")
