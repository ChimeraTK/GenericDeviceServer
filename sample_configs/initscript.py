#! /usr/bin/python3

import deviceaccess as da
import numpy as np

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()

acc = d.getOneDRegisterAccessor(np.uint32, 
    'BSP/SCRATCH')
acc[0] = 42
acc.write()


# ------------- not shown in talk ----------
import os

fid = d.read("BSP/ID")
if fid != 0:
    # Forward to CG's script for real hw initialization
    err=os.system("./main.py -t initialize -s 3 -c dwc8vm1")
    exit(err!=0)
else:
    print ("initscript.py for dummy done")
