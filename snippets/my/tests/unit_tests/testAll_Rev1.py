#!/usr/bin/python3

import time
import os.path
import sys
import random
import threading
import copy
import re

# these are pip or external python files?
import serial
import Queue
import pipes

testGM   = True
testPM   = True

iters  = 20
gmMax  = 1 * iters
pmMax  = 8 * iters
genMax = 4 * iters

threads    = []
sendQ      = Queue.Queue()

tagGM  = b'G:'
tagPM  = b'P:'
tagCmd = b'C:'

ackQ   = Queue.Queue()


# need for reliability, update every command that is sent
sendCnt = 0

######################################################################
def serial_init():
    print ("Info: initialize serial port...")
    sys.stdout.flush()
    if os.name == 'nt':
        s = serial.Serial('COM11')

    else: # Linux
        if os.path.exists('/dev/ttyUSB0'):
            s = serial.Serial('/dev/ttyUSB0')
        elif os.path.exists('/dev/ttyUSB1'):
            s = serial.Serial('/dev/ttyUSB1')
        else:
            print ("ERROR: I don't see /dev/ttyUSB0 or /dev/ttyUSB1, aborting");
            exit(2);

    s.bytesize = 8
    s.stopbits = 1
    s.parity   = serial.PARITY_ODD 
    s.baudrate = 9600
    s.timeout  = 120     # is this enough for GMHome?
    s.writeTimeout = 2.0
    print ("Info: Done")
    sys.stdout.flush()
    return s

######################################################################
def getFields( pm, resp ):
    tag = resp[0:2]
    if tag == tagGM:
        res = (" %cGM      ") % (pm)
    elif tag == tagPM:
        res = ("      %cPM ") % (pm)
    else:
        res = " ???   ??? "
    
    # print ("DBG " + res)
    return res

def myToInt ( bts ):
    dec0   = (b'0'[0])
    space  = (b' '[0])
    mult = 1
    res  = 0
    while len(bts) > 0:
        i = bts[-1]
        if i != space:
            res += mult * (i - dec0)
        mult *= 10
        bts = bts[:-1]
    return res

######################################################################
def showRsp( resp ):
    # print (("DBG4: resp = %s") % (resp))
    dbgInfo = getFields( "-", resp )
    print ( ("%s %s                              Rsp = %s") % (time.ctime(),dbgInfo,resp.rstrip()) )

class ThreadUnit( threading.Thread ):
    # ho boy :)  derive from threading class 
    def __init__( self, tag, cmds, loopCount, sleepValue  ):
        threading.Thread.__init__(self)
        self.respQ    = Queue.Queue()
        self.commands = cmds
        self.sleep    = sleepValue
        self.tag      = tag
        self.hitList  = []
        self.lastInx  = 0
        self.maxLoop  = loopCount
        self.stopbit  = False

        global threads
        threads.append( self )

    # put responses in here
    def put( self, mess ):
        self.respQ.put( mess )

    def stop( self ):
        self.stopbit  = True

    # all units do the same thing (with a few variables)
    # shuffle a list of all command we can send (and expect 
    # responses from, at least on a PLC with no motors attached
    # for now
    def run( self ):
        global sendQ

        self.lastInx = len(self.commands)
        for j in range( self.lastInx ):
            self.hitList.append( j )

        for j in range( self.maxLoop ):
            random.shuffle( self.hitList )

            for i in range ( self.lastInx ):
                # queue up a command
                
                if self.stopbit:
                    return

                ## >> send commands from PM or GM to sendQ
                cmd = self.commands[ self.hitList[i] ]

                if cmd == b'Go':
                    # pick 45, 45+90, 45+180, or 45+270 (randomly?)
                    val = random.randint(0,3)
                    if val == 0: 
                        cmd = cmd + b'45'
                    elif val == 1: 
                        cmd = cmd + b'135'
                    elif val == 2: 
                        cmd = cmd + b'225'
                    else: 
                        cmd = cmd + b'315'

                finalCmd = self.tag + b' ' +  cmd 
                # print ("DBG1: enq to senqQ: " + str(finalCmd,'utf-8'))
                sendQ.put( finalCmd + b'\r' )

                # wait for response
                resp = self.respQ.get()
                showRsp( resp )
                time.sleep(self.sleep)
                ## << wait for response

        print (("Info: thread %s complete") % (self.tag))


######################################################################
# sending commands needs to be serialized because we need to have a
# small delay after each command is send because the PLC can't push
# back when its not ready

class ThreadSend( threading.Thread ):
    def __init__( self, tag, totalOps, sleepDelay  ):
        threading.Thread.__init__(self)
        self.tag        = tag
        self.totalLoops = totalOps
        self.sleep      = sleepDelay
        self.stopbit    = False

        global threads
        threads.append( self )

    def stop( self ):
        self.stopbit  = True

    def run( self ):
        global ser, sendQ, ackQ, sendCnt

        for i in range( self.totalLoops ):
            mess    = sendQ.get()
            dbgInfo = getFields( "+", mess )

            # send message
            print ( ("%s %s %d Snd = %s") % (time.ctime(),dbgInfo,sendCnt,mess) )
            ser.write( mess )  
            time.sleep( 0.3 )  # major yuck

            if self.stopbit:
                return

            # this thread exists entirely to make sure there is a small sleep
            # after each command is sent
            # time.sleep( self.sleep )


        print (("Info: thread %s complete") % (self.tag))

######################################################################
gmcommands = [
    b'LedFrontOn',
    b'LedFrontOff',
    b'D65FrontOn',
    b'D65FrontOff',
    b'TL84FrontOn',
    b'TL84FrontOff',
    b'LedBackOn',
    b'LedBackOff',
    b'D65BackOn',
    b'D65BackOff',
    b'TL84BackOn',
    b'TL84BackOff',
#    b'HalogenFrontOn',
#    b'HalogenFrontOff',
#    b'HalogenBackOn',
#    b'HalogenBackOff',
    b'FrontCameraPresent',
    b'BackCameraPresent',
    b'Go',
    b'Home',
    b'FpLedTopOn',
    b'FpLedTopOff',
    b'RevNumber'
]

pmcommands = [
    b'CameraPresent',
    b'Go',
    b'Home',
    b'ELOn',
    b'ELOff',
    b'FpLedBottomOn',
    b'FpLedBottomOff',
    b'RevNumber'
]

######################################################################
# initialize serial port
ser     = serial_init()

# create a thread for each of the GM, PM, Ms commands each uses a
# mutex locked shared sendQueue, but has their own response queue
# (which is filled by a single thread recieving responses below)

random.seed(0);
sendDelay = 0.3 # * 300ms for 9600 baud :P

######################################################################
totalOps = 0;
if testGM:
    totalOps += gmMax*len(gmcommands)

if testPM:
    totalOps += pmMax*len(pmcommands)

# create threads as needed
if testGM or testPM:
    threadSnd = ThreadSend( "Snd", totalOps, sendDelay )
    print ("Start Send thread...")
    threadSnd.start()

# send a reset in case I've left it screwed up
print ("Info: Reset" )
sys.stdout.flush()
ser.write( b'C: Reset\r' )

ser.readline()
print ("Info: ResetComplete" )
sys.stdout.flush()
sendCnt = 1

######################################################################
if testGM:
    threadGM = ThreadUnit(  tagGM, gmcommands,  gmMax,  0.1 )
    print ("Info: Start GM thread...")
    sys.stdout.flush()
    threadGM.start()

if testPM:
    threadPM = ThreadUnit(  tagPM,  pmcommands,  pmMax,  0.1 )
    print ("Info: Start PM thread...")
    sys.stdout.flush()
    threadPM.start()
    
########################################
# get responses
rspNumLast = -1

while True:
    resp = ser.readline()
    resp = resp[0:-1]
    # print (("DBG: resp = %s") % (resp) )

    # resp = b'P: Ok >   2\n'
    if resp[0:2] == tagCmd:
        num = int( resp[-1] ) - 0x30
        cmd = resp[3:5]

        # okay or retry?
        if cmd == b'Ok':
            ackQ.put( ('Ok',num) )
        else:
            print (("DBG2: %s  (%s , %d)") % (resp,cmd,num))
            ackQ.put( ('Error',num) )

    elif testGM and (resp[0:2] == tagGM):
        threadGM.put( resp )
        
    elif testPM and (resp[0:2] == tagPM):
        threadPM.put( resp )

    else:
        # command not received properly or status corrupted
        print (("ERROR: failure response: %s") % (resp))
        for t in threads:
            t.stop()
        break


######################################################################
# wait for threads to complete
# close threads we openend
for t in threads:
    t.join()

ser.close()

