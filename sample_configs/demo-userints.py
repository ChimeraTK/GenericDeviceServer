#! /usr/bin/python3

import deviceaccess as da
import numpy as np

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()
d.activateAsyncRead()

trigger = d.getOneDRegisterAccessor(np.uint32, 'APP/ISR/TRIGGER',
    accessModeFlags = [da.AccessMode.wait_for_new_data])

# read initial value: this is polled
trigger.read()

print ('waiting on APP/ISR/TRIGGER')
i = 0
while True :
    trigger.read()
    print('Trigger event ' + str(i))
    i += 1
    
