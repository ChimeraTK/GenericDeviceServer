#! /usr/bin/python3

import deviceaccess as da
import numpy as np

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()
d.activateAsyncRead()

triggerCounters = d.getOneDRegisterAccessor(np.uint32, 'TIMING/TRIGGER_CNT_IRQ',
    accessModeFlags = [da.AccessMode.wait_for_new_data])

# read initial value: this is polled
triggerCounters.read()

print ('waiting on TRIGGER_CNT_IRQ')
while True :
    triggerCounters.read()
    print('Trigger, counter[1] = ' + str(triggerCounters[1]))
    
