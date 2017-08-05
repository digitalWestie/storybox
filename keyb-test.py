import atexit
import logging
import subprocess
import sys
import time
import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO

def logTouched(opts={}):
    print(opts)

# Define mapping of capacitive touch pin presses to keyboard button presses.
KEY_MAPPING = {
    0: { 'fn': logTouched,   'params': {"pin":"0"} }, 
    1: { 'fn': logTouched,   'params': {"pin":"1"} },
    2: { 'fn': logTouched,   'params': {"pin":"2"} },
    3: { 'fn': logTouched,   'params': {"pin":"3"} },
    4: { 'fn': logTouched,   'params': {"pin":"4"} },
    5: { 'fn': logTouched, 'params': {"pin":"5"} },
    6: { 'fn': logTouched, 'params': { "action": "volumeup" } },
    7: { 'fn': logTouched, 'params': { "action": "volumedown" } },
    8: { 'fn': logTouched, 'params': { "pin":"8" } }
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
    if (time.time() - timeSinceChange) > 10:
      print "phone has been in same state for 6 mins"
      timeSinceChange = time.time()
      #send cmd

    # Read touch state.
    touched = cap.touched()
    # Emit key presses for any touched keys.
    for pin, key in KEY_MAPPING.iteritems():
        # Check if pin is touched.
        pin_bit = 1 << pin

        if (pin == 8):
            # Check if transitioned from not touched to touched.
            if touched & pin_bit and not last_touched & pin_bit:
                print "Touching phone"
                timeSinceChange = time.time()
            # Next check if transitioned from touched to not touched.
            if not touched & pin_bit and last_touched & pin_bit:
                print "Released phone"
                timeSinceChange = time.time()
            # Update last state and wait a short period before repeating.
            last_touched = touched

        elif (touched & pin_bit):
            logging.debug('Input {0} touched.'.format(pin))
            fn = KEY_MAPPING[pin]['fn']
            p = KEY_MAPPING[pin]['params']
            fn(p)
