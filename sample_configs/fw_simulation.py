#! /usr/bin/python3

import deviceaccess as da
import numpy as np
import time

da.setDMapFilePath('devices.dmap')
d = da.Device('ADC_BOARD')
d.open()

triggerCounters = d.getOneDRegisterAccessor(np.uint32, 
    'TIMING/TRIGGER_CNT/DUMMY_WRITEABLE')

irq0 = d.getOneDRegisterAccessor(np.uint32, '/DUMMY_INTERRUPT_0')
appISR = d.getOneDRegisterAccessor(np.uint32, '/APP/ISR')

demoDoubleBuff=False
activeBuf = d.getOneDRegisterAccessor(np.uint32, '/DAQ/ACTIVE_BUF/DUMMY_WRITEABLE')
doubleBufEna = d.getOneDRegisterAccessor(np.uint32, '/DAQ/DOUBLE_BUF_ENA')
buf0Acc = d.getTwoDRegisterAccessor(np.int32, 'DAQBUF/DAQ_CTRL_BUF0/DUMMY_WRITEABLE')
buf1Acc = d.getTwoDRegisterAccessor(np.int32, 'DAQBUF/DAQ_CTRL_BUF1/DUMMY_WRITEABLE')

first_time = time.time()
loopCount = 0

print ('entering fw simulation loop')
while True :
    triggerCounters[0] += 1
    triggerCounters.write()
    # before triggereing interrupt line 0, set first bit of interrupt status register APP.ISR: 
    # then only APP.ISR.TRIGGER should trigger, not APP.ISR.DAQ or APP.ISR.RTM
    appISR[0] = 1
    appISR.write()
    irq0.write()
    
    startVal = triggerCounters[0]
    alen = 16384
    newVals = 1000*np.sin(.001*(np.arange(0,alen)+1000*startVal))
    
    if demoDoubleBuff:
        activeBuf.read()
        if activeBuf[0] == 0:
            # in order to show corrupted data, we need to update slowly, so iterate over array
            for i in range(0,alen):
                buf0Acc[10][i] = newVals[i]
                if i % 1024 == 1023:
                    buf0Acc.write()
        else:
            # in order to show corrupted data, we need to update slowly, so iterate over array
            for i in range(0,alen):
                buf1Acc[10][i] = newVals[i]
                if i % 1024 == 1023:
                    buf1Acc.write()
        doubleBufEna.read()
        if doubleBufEna[0]:
            #print ("switch buffer")
            activeBuf[0] = 1 - activeBuf[0]
            activeBuf.write()
    else:
        for i in range(0,alen):
            buf0Acc[10][i] = newVals[i]
        buf0Acc.write()
        
    loopCount += 1
    cur_time = time.time()
    time.sleep(max(loopCount*0.100 - (cur_time - first_time), 0))
