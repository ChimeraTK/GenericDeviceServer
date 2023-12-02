#!/bin/bash

jddd &

cp devices.dmap.xdma devices.dmap
cp generic_chimeratk_server_configuration.xml.irq generic_chimeratk_server_configuration.xml

rm CMakeCache.txt
cmake  -DADAPTER="DOOCS"  -S ../GenericDeviceServer/ .
make -j4
./doocs-generic-chimeratk-server01
