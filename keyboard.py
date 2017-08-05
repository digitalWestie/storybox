# Adafruit Raspberry Pi MPR121 Keyboard Example
# Author: Tony DiCola
#
# Allows you to turn touches detected by the MPR121 into key presses on a
# Raspberry Pi.
#
# NOTE: This only works with a Raspberry Pi right now because it depends on some
# specific event detection logic in the RPi.GPIO library.
#
# Dependencies
# ============
#
# Make sure you have the required dependencies by executing the following commands:
#   sudo apt-get update
#   sudo apt-get install build-essential python-dev python-pip libudev-dev
#   sudo pip install python-uinput
#
# Also make sure you have installed the Adafruit Python MPR121 library by running
# its setup.py (in the parent directory):
#   sudo python setup.py install
#
# Usage
# =====
#
# To use this program you first need to connect the MPR121 board to the Raspberry
# Pi (either connect the HAT directly to the Pi, or wire the I2C pins SCL, SDA to
# the Pi SCL, SDA, VIN to Pi 3.3V, GND to Pi GND).  If you aren't using the HAT
# version of the board you must connect the IRQ pin to a free digital input on the
# Pi (the default is 26).
#
# Next define the mapping of capacitive touch input presses to keyboard
# button presses.  Scroll down to the KEY_MAPPING dictionary definition below
# and adjust the configuration as described in its comments.
#
# If you're using a differnet pin for the IRQ line change the IRQ_PIN variable
# below to the pin number you're using.  Don't change this if you're using the
# HAT version of the board as it's built to use pin 26 as the IRQ input.
#
# Finally run the script as root:
#   sudo python keyboard.py
#
# Try pressing buttons and you should see key presses made on the Pi!
#
# Press Ctrl-C to quit at any time.
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------- 
# This software has been modified for Storybox application by author(s): Rory Gianni

import atexit
import logging
import subprocess
import sys
import time
import csv
from datetime import datetime
import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO
from xbmcjson import XBMC, PLAYER_VIDEO

def checkPlayLog():
  try: 
    with open('/media/pi/storybox/playlog.csv', 'rb') as csvfile:
      reader = csv.reader(csvfile)
      row_count = sum(1 for row in reader)
    if row_count == 0:
      fields=['time','title','author', 'file']
      addToPlayLog(fields)
  except Exception as error:
    print "\nCouldn't read playlog.csv file, please make sure it exists on the USB storybox directory\n", str(error)
    sys.exit()

def addToPlayLog(row):
  with open('/media/pi/storybox/playlog.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(row)

def maxVolume():
  xbmc.Application.SetMute({"mute": False })
  xbmc.Application.SetVolume({ "volume": 100 })

time.sleep(7)
checkPlayLog()

xbmc = XBMC("http://localhost:8080/jsonrpc", "kodi", "kodi")
print xbmc.JSONRPC.Ping()
maxVolume()

def enterLog(opts={}):
  xbmc.Input.Select({})
  maxVolume()
  time.sleep(1.5)
  active = xbmc.Player.GetActivePlayers()
  if (len(active['result']) != 0):
    item = xbmc.Player.GetItem({ "playerid": active['result'][0]['playerid'],  "properties": ["title", "artist", "file"] })
    row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), item['result']['item']['title'], ' '.join(item['result']['item']['artist']), item['result']['item']['file']]
    addToPlayLog(row)

def logTouched(opts={}):
    print(opts)

def stopBack(opts={}):
    active = xbmc.Player.GetActivePlayers()
    if (len(active['result']) == 0):
        xbmc.Input.Home()
    else:
        for result in active['result']:
            del result['type']
            xbmc.Player.Stop(result)

def volumeChange(params):
    xbmc.Input.ExecuteAction(params)
    #time.sleep(0.1)
    xbmc.Input.ExecuteAction(params)
    xbmc.Input.ExecuteAction(params)
    xbmc.Input.ExecuteAction(params)

# Define mapping of capacitive touch pin presses to keyboard button presses.
KEY_MAPPING = {
    0: { 'fn': xbmc.Input.Up,     'params': {} }, 
    1: { 'fn': xbmc.Input.Down,   'params': {} },
    2: { 'fn': xbmc.Input.Left,   'params': {} },
    3: { 'fn': xbmc.Input.Right,  'params': {} },
    4: { 'fn': stopBack,          'params': {} },
    5: { 'fn': enterLog, 'params': {} },
    6: { 'fn': logTouched, 'params': { "pin":"6" } },
    7: { 'fn': logTouched, 'params': { "pin":"7" } },
    8: { 'fn': logTouched, 'params': { "pin":"8" } },
    9: { 'fn': volumeChange, 'params': { "action": "volumedown" } },
    10: { 'fn': volumeChange, 'params': { "action": "volumeup" } }
}

# Input pin connected to the capacitive touch sensor's IRQ output.
# For the capacitive touch HAT this should be pin 26!
IRQ_PIN = 26

# Don't change the below values unless you know what you're doing.  These help
# adjust the load on the CPU vs. responsiveness of the key detection.
MAX_EVENT_WAIT_SECONDS = 0.7
EVENT_WAIT_SLEEP_SECONDS = 0.1

# Uncomment to enable debug message logging (might slow down key detection).
#logging.basicConfig(level=logging.DEBUG)

# Make sure kernel modules is loaded.
subprocess.check_call(['modprobe', 'i2c_bcm2708'])

# Setup the MPR121 device.
cap = MPR121.MPR121()
if not cap.begin():
    print('Failed to initialize MPR121, check your wiring!')
    sys.exit(1)

# Configure GPIO library to listen on IRQ pin for changes.
# Be sure to configure pin with a pull-up because it is open collector when not
# enabled.
GPIO.setmode(GPIO.BCM)
GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(IRQ_PIN, GPIO.FALLING)
atexit.register(GPIO.cleanup)

# Clear any pending interrupts by reading touch state.
cap.touched()

timeSinceChange = time.time()

last_touched = cap.touched()


# Event loop to wait for IRQ pin changes and respond to them.
print('Press Ctrl-C to quit.')
while True:
    # Wait for the IRQ pin to drop or too much time ellapses (to help prevent
    # missing an IRQ event and waiting forever).
    start = time.time()
    while (time.time() - start) < MAX_EVENT_WAIT_SECONDS and not GPIO.event_detected(IRQ_PIN):
        time.sleep(EVENT_WAIT_SLEEP_SECONDS)

    #Check if phone hasn't moved for a while
    if (time.time() - timeSinceChange) > 6000:
      print "phone has been in same state for 6 mins"
      stopBack()
      stopBack()
      timeSinceChange = time.time()
      #send cmd
    
    # Read touch state.
    touched = cap.touched()
    # Emit key presses for any touched keys.
    for pin, key in KEY_MAPPING.iteritems():
        # Check if pin is touched.
        pin_bit = 1 << pin

        if (touched & pin_bit):
            timeSinceChange= time.time()
            logging.debug('Input {0} touched.'.format(pin))
            fn = KEY_MAPPING[pin]['fn']
            p = KEY_MAPPING[pin]['params']
            fn(p)
