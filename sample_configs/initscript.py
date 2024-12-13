#! /usr/bin/python3

import deviceaccess as da
import numpy as np

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()


# ------------- begin not shown in talk ----------
import os

fid = d.read("BSP/ID")
if fid != 0:
    # Forward to CG's script for real hw initialization
    err=os.system("./main.py -t initialize -s 4 -c dwc8vm1")
    exit(err!=0)
else:
# ------- end not shown in talk 
    
    acc = d.getOneDRegisterAccessor(np.uint32, 
        'TIMING/DIVIDER_VALUE')
    acc[0] = 12499999
    acc.write()    
    
    
    print ("initscript.py for dummy done")



