#!/bin/bash

touch /media/pi/storybox/playlog.csv

sudo modprobe i2c_bcm2708

lxterminal -e sudo python ~/storybox/keyboard.py

lxterminal -e kodi

