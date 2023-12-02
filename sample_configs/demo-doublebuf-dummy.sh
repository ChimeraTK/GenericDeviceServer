#!/bin/bash


cp devices.dmap.dummy devices.dmap

QtHardMon devices.dmap &

./fw_simulation.py 

