#!/bin/bash

# this is step 1 + step 2 combined, which requires that xDMA with interrupts + DMA are working at the same time
cp devices.dmap.xdma devices.dmap
cp generic_chimeratk_server_configuration.xml.irq generic_chimeratk_server_configuration.xml
./opcua-generic-chimeratk-server01

