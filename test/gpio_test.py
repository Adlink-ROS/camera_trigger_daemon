#!/usr/bin/env python

# Author: Brendan Le Foll <brendan.le.foll@intel.com>
# Copyright (c) 2014 Intel Corporation.
#
# SPDX-License-Identifier: MIT
#
# Example Usage: Triggers ISR upon GPIO state change

import mraa
import time
import sys


# inside a python interrupt you cannot use 'basic' types so you'll need to use
# objects
def isr_routine(gpio):
    print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
    led.setBrightness(1)
    time.sleep(0.25)
    led.setBrightness(0)
    time.sleep(0.25)

# GPIO
pin = 5 if len(sys.argv) < 2 else int(sys.argv[1])

led_num = 0 if len(sys.argv) < 3 else int(sys.argv[2])

try:
    # initialise GPIO
    x = mraa.Gpio(pin)
    time.sleep(0.05)

    # initialise LED
    led = mraa.Led(led_num)
    time.sleep(0.05)

    print("Starting ISR for pin " + repr(pin))

    # set direction and edge types for interrupt
    x.dir(mraa.DIR_IN)
    time.sleep(0.05)
    x.isr(mraa.EDGE_RISING, isr_routine, x)
    time.sleep(0.05)

    # wait until ENTER is pressed
    var = input("Press ENTER to stop\n")
    x.isrExit()

except ValueError as e:
    print(e)