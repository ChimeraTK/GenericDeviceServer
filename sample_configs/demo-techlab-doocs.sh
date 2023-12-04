#!/bin/bash

jddd &

rm CMakeCache.txt
cmake  -DADAPTER="DOOCS"  -S ../GenericDeviceServer/ .
make -j4

cp devices.dmap.xdma devices.dmap

./doocs-generic-chimeratk-server01
