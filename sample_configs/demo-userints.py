#! /usr/bin/python3

import deviceaccess as da
import numpy as np

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()
d.activateAsyncRead()

triggerCounters = d.getOneDRegisterAccessor(np.uint32, 'TIMING/TRIGGER_CNT',
    accessModeFlags = [da.AccessMode.wait_for_new_data])

#acc2 = d.getTwoDRegisterAccessor(np.uint32, '/APP0/DAQ_CTRL_BUF0',
#    accessModeFlags = [da.AccessMode.wait_for_new_data])


# read initial value: this is polled
triggerCounters.read()

while True :
    triggerCounters.read()
    print('Trigger, counter[2] = ' + str(triggerCounters[2]))
    
    #acc2.read()
    #print('acc2 triggered')
