#! /usr/bin/python3

import deviceaccess as da
import numpy as np

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()

triggerCounters = d.getOneDRegisterAccessor(np.uint32, 
    'TIMING/TRIGGER_CNT/DUMMY_WRITEABLE')

while True :
    triggerCounters[1] += 1
    triggerCounters.write()
