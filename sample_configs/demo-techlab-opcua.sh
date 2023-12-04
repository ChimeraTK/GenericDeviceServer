#!/bin/bash

#rm CMakeCache.txt
#cmake  -DADAPTER="OPCUA"  -S ../GenericDeviceServer/ .
#make -j4

cp devices.dmap.xdma devices.dmap

./opcua-generic-chimeratk-server01
