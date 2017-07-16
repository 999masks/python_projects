#!/usr/bin/python2.7

import time
import os.path
import serial
import random

def serial_init():
    # open port
    global ser
    if os.path.exists('/dev/ttyUSB0'):
        ser = serial.Serial('/dev/ttyUSB0')
    elif os.path.exists('/dev/ttyUSB1'):
        ser = serial.Serial('/dev/ttyUSB1')
    else:
        print ("ERROR: I don't see /dev/ttyUSB0 or /dev/ttyUSB1, aborting");
        exit(2);

    ser.parity   = serial.PARITY_ODD 
    ser.timeout  = 20
    ser.stopbits = 1
    ser.baudrate = 9600
    ser.bytesize = 8

serial_init();
ser.flushInput()

commands = [
    b'LedFrontOn\r',
    b'LedFrontOff\r',
    b'D65FrontOn\r',
    b'D65FrontOff\r',
    b'TL84FrontOn\r',
    b'TL84FrontOff\r',
    b'LedBackOn\r',
    b'LedBackOff\r',
    b'D65BackOn\r',
    b'D65BackOff\r',
    b'TL84BackOn\r',
    b'TL84BackOff\r',
    b'ELOn\r',
    b'ELOff\r',
    b'FpLedTopOn\r',
    b'FpLedTopOff\r',
    b'FpLedBottomOn\r',
    b'FpLedBottomOff\r',
    b'FrontCameraPresent\r',
    b'BackCameraPresent\r',
    b'PMCameraPresent\r',
    b'PMPos\r',
    b'GMPos\r',
    b'RevNumber\r'
    ]
#    b'-reset\r',
#    b'-badcommand\r'


def sendMess( mess ):
    ser.write(mess)
    print (("%s Send %s") % (time.ctime(),mess))
    time.sleep(0.05)

def getMess():
    resp = ser.readline()
    print ( ("%s Ack = %s") % (time.ctime(),resp.rstrip()) )
    return resp

######################################################################
random.seed(0);
lastInx = len(commands) - 1
hitList = []

for x in range(0,20):
    # make sure we hit them all but using an randomized list of all entries
    print (">> Randomizing list")
    hitList = range( 0,lastInx )
    random.shuffle( hitList )

    for i in range (0,lastInx):
        mess = commands[ hitList[i] ]

        if mess == b'-reset\r':
            # this will hang if there no box there
            # if there is, home will probably not be done yet - I hope
            sendMess(b'GMHome\r')
            time.sleep(2)
            sendMess(b'Reset\r')
            getMess()

        else:
            sendMess(mess)
            getMess()


ser.close()


