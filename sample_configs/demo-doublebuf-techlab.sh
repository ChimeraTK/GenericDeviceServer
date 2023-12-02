#!/bin/bash


cp devices.dmap.xdma devices.dmap

QtHardMon devices.dmap &

echo "you can set TIMING/DIVIDER_VALUE = 1249999 for updates @ 100Hz"
