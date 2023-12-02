#!/bin/bash

cp devices.dmap.xdma devices.dmap
cp generic_chimeratk_server_configuration.xml.irq generic_chimeratk_server_configuration.xml

#rm CMakeCache.txt
#cmake  -DADAPTER="OPCUA"  -S ../GenericDeviceServer/ .
#make -j4
./opcua-generic-chimeratk-server01
