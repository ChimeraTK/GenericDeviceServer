#!/bin/bash

./fw_simulation.py &

cp devices.dmap.dummy devices.dmap

/usr/bin/opcua-generic-chimeratk-server02
