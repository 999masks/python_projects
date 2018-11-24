#!/usr/bin/python3

import time
import os.path
import sys
import random
import threading
import copy
import re

import serial   # PLC serial interface routines
import Queue    # thread safe fifo

######################################################################
def serial_init():
    global plc
    print ("Info: initialize serial port...")
    sys.stdout.flush()

    # check to see if either exists, uses whichever on is there
    if os.path.exists('/dev/ttyUSB0'):
        plc = serial.Serial('/dev/ttyUSB0')
    elif os.path.exists('/dev/ttyUSB1'):
        plc = serial.Serial('/dev/ttyUSB1')
    else:
        print ("ERROR: I don't see /dev/ttyUSB0 or /dev/ttyUSB1, aborting");
        exit(2);

    # this has to match the PLC
    plc.abytesize    = 8
    plc.stopbits     = 1
    plc.parity       = serial.PARITY_ODD 
    plc.baudrate     = 9600
    plc.timeout      = 10
    plc.writeTimeout = 2.0
    plc.flushInput()
    time.sleep(0.1)

serial_init()  # defines plc
plc.flushInput()

plc.write( b'C: Reset\r' )
mess = plc.readline()
print(mess)

plc.close()
