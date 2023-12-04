#!/bin/bash

./fw_simulation.py &

cp devices.dmap.dummy devices.dmap

#rm CMakeCache.txt
#cmake  -DADAPTER="OPCUA"  -S ../GenericDeviceServer/ .
#make -j4
./opcua-generic-chimeratk-server01
