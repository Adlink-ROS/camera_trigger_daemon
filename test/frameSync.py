#!/bin/python3

import time
import sys
sys.path.append("/opt/adlink/neuron-sdk/neuron-library/lib/python3.6/dist-packages")
import mraa

try:
    gpio_1 = mraa.Gpio(51)
    gpio_2 = mraa.Gpio(52)
    gpio_3 = mraa.Gpio(53)
    gpio_4 = mraa.Gpio(54)
    time.sleep(0.5)
    gpio_1.dir(mraa.DIR_OUT)
    gpio_2.dir(mraa.DIR_OUT)
    gpio_3.dir(mraa.DIR_OUT)
    gpio_4.dir(mraa.DIR_OUT)

except ValueError as e:
    print(e)

print("success to init camera")
time.sleep(0.5)
hz = 10
interval = 1/hz
min_fsync_interval = 0.005
wait_idle = interval - min_fsync_interval

for i in range(10000000):
    gpio_1.write(1)
    gpio_2.write(1)
    gpio_3.write(1)
    gpio_4.write(1)
    time.sleep(min_fsync_interval)
    gpio_1.write(0)
    gpio_2.write(0)
    gpio_3.write(0)
    gpio_4.write(0)
    time.sleep(wait_idle)
