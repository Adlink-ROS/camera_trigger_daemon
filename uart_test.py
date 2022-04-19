#!/usr/bin/env python

# Author: Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>
# Copyright (c) 2018 Linaro Ltd.
#
# SPDX-License-Identifier: MIT
#
# Example Usage: Sends data through UART

import mraa
import time
import sys

# serial port
port = "/dev/ttyUSB4"

data = []

# initialise UART
uart = mraa.Uart(port)
time.sleep(0.05)

# Set UART parameters
uart.setBaudRate(115200)
time.sleep(0.05)
uart.setMode(8, mraa.UART_PARITY_NONE, 1)
time.sleep(0.05)
uart.setFlowcontrol(False, False)
time.sleep(0.05)

print(uart.getDevicePath())
# recive data through UART
while(True):
    if uart.dataAvailable():
        data_byte = uart.readStr(38)
        data_byte = data_byte.split(",")
        print(data_byte,"\n")