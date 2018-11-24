#!/usr/bin/python2

######################################################################
#
# author: steve@light.co
# date:   Dec 15, 2016
#
# purpose: support run of the GM and PM motors asynchronous to each
#          other (sort of).  They have to talk to the PLC serially,
#          but provide thread safe queues to read and write such that
#          PM and GM can run separate.
######################################################################

# import time
# import copy
# import re
# import random
import os.path
import sys
import threading


######################################################################
debugSendRcvr = True
realSerial    = False

gmRange = 10
pmRange = 20

######################################################################
import BreakableQueue

# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
if realSerial:
    # noinspection PyUnresolvedReferences
    import Serial
else:
    from FakePLC import *


# noinspection PyUnboundLocalVariable,PyUnresolvedReferences
def serial_init():
    global realSerial
    if realSerial:
        print ("Info: initialize serial port...")
        sys.stdout.flush()
        
        # check to see if either exists, uses whichever on is there
        if os.path.exists('/dev/ttyUSB0'):
            tplc = serial.Serial('/dev/ttyUSB0')
        elif os.path.exists('/dev/ttyUSB1'):
            tplc = serial.Serial('/dev/ttyUSB1')
        else:
            print ("ERROR: I don't see /dev/ttyUSB0 or /dev/ttyUSB1, aborting")
            exit(2)
            
        # this has to match the PLC
        tplc.abytesize    = 8
        tplc.stopbits     = 1
        tplc.parity       = serial.PARITY_ODD
        tplc.baudrate     = 9600
        tplc.timeout      = 10
        tplc.writeTimeout = 2.0
        tplc.flushInput()
        return tplc

    else:
        tplc = FakePLC()
        tplc.start()
        return tplc
        

######################################################################
def printT ( strn ):
    """print with timestamp"""
    print( time.ctime() + "  " + strn )

class RespRetried(Exception):
    """Response from PLC malformed"""
    pass

######################################################################
# a bit long winded, but make sure I keep a copy of commands that are outstanding
# so if we get a corruption, I know who the likely candidates are
class RetryState:
    def __init__( self, send ):
        self.ip         = [None,None,None]
        self.mutex      = threading.Lock()
        self.send       = send

    def acquire( self ):
        self.mutex.acquire()

    def release( self ):
        self.mutex.release()

    def getInx( self, cmd ):
        if cmd[0:2] == "G:":
            return 0
        elif cmd[0:2] == "P:":
            return 1
        elif cmd[0:2] == "C:":
            return 2
        else:
            return -1
        
    def set( self, cmd ):
        self.inx = self.getInx( cmd )
        self.acquire()
        self.ip[self.inx] = cmd
        self.release()

    def clear( self, resp ):
        self.inx = self.getInx( resp )

        if self.inx == -1:
            for i in range(0,3):
                if self.ip[self.inx] is not None:
                     self.send.put( self.ip[self.inx], updateState=False )
            raise RespRetried

        self.acquire()
        self.ip[self.inx] = None
        self.release()            

# yes define this in main/top level for now :P


######################################################################
class ThreadSend( threading.Thread ):

    def __init__( self, ser ):
        super(ThreadSend,self).__init__()
        self.sendQ = BreakableQueue.BreakableQueue()
        self.ser     = ser 
        self._printX("*** thread starting")
        
    def _printX( self, strn ):
        global debugSendRcvr
        if debugSendRcvr:
            printT("Send: " + strn )

    def stop( self ):
        self._printX("stop called")
        self.sendQ.stop()

    def put( self, cmd, updateState=True ):
        global retryState
        if updateState:
            retryState.set( cmd )
        self.sendQ.put( cmd )

    def run( self ):
        while True:
            try:
                self.cmd = self.sendQ.get()
                self._printX( "wrt: " + self.cmd )
                self.ser.write( self.cmd.encode('utf-8') + b'\r' )

                # special case for clean stop (for testing mostly)
                if self.cmd == "G: Stop":
                    raise BreakableQueue.QueueStop

                time.sleep(0.3)
            except BreakableQueue.QueueStop:
                self._printX("*** thread ending")
                return
            
######################################################################
class ThreadRcvr( threading.Thread ):

    def _printX( self, strn ):
        global debugSendRcvr
        if debugSendRcvr:
            printT("Rcvr: " + strn )

    def __init__( self, ser ):
        super(ThreadRcvr,self).__init__()
        self.qGM = BreakableQueue.BreakableQueue()
        self.qPM = BreakableQueue.BreakableQueue()
        self.qC  = BreakableQueue.BreakableQueue()
        self.ser = ser
        self.stopbit = False
        self._printX("*** thread starting")
        
    def stop (self):
        self.stopbit = True
        self.qGM.stop()
        self.qPM.stop()
        self.qC.stop()
        
    def getGM( self ):
        try:
            return self.qGM.get()
        except BreakableQueue.QueueStop:
            return None

    def getPM( self ):
        try:
            return self.qPM.get()
        except BreakableQueue.QueueStop:
            return None

    def getC( self ):
        try:
            return self.qC.get()
        except BreakableQueue.QueueStop:
            return None
        except:
            asdf

    def _readline( self ):
        for i in range(0,10):
            try:
                self.resp = self.ser.readline().decode().rstrip()

                # raise exception we we had to retry this
                # so just go get the next response :)
                global retryState
                retryState.clear( self.resp )

                if self.resp == "G: Stop":
                    return None
                elif self.resp != "":
                    self._printX("readline: resp = " + self.resp)
                    return self.resp
                # print("readline retry")
                
            except:  
                # corrupted data
                self._printX("Readline corrupted data seen")
                return None

        return None

    def run( self ):
        while True:
            self.resp = self._readline()
            if self.resp is None:
                break

            self._printX("run => resp = " + self.resp)

            self.tag = self.resp[0:2]
            self.cmd = self.resp[3:]
            if self.tag == "G:":
                self.qGM.put(self.cmd)
            elif self.tag == "P:":
                self.qPM.put(self.cmd)
            elif self.tag == "C:":
                self.qC.put(self.cmd)
            else:
                self._printX("ERROR: unknown response (" + self.tag + ") (" + self.cmd + ")")
                break

        self._printX("*** thread ending")

######################################################################
class ThreadGM( threading.Thread ):

    def _printX( self, strn ):
        printT("GM:   " + strn )

    def __init__( self, send, rcvr ):
        super(ThreadGM,self).__init__()
        self.send = send
        self.rcvr = rcvr
        self.stopbit = False
        self.hitlist = ["0.0","45.0","135.0","180.0","225.0","315.0"]
        self._printX("*** thread starting")
        
    def run( self ):
        global gmRange
        random.shuffle( self.hitlist )
        for i in range(1, gmRange):
            self.cmd = "G: Go" + self.hitlist[ i % 6 ]
            self._printX   ( "snd = " + self.cmd )
            self.send.put ( self.cmd )
            self.resp = self.rcvr.getGM()
            if self.resp is None:
                self._printX("WARNING: no response")
            else:
              self._printX("rsp = " + self.resp)

        self._printX("*** thread ending")

######################################################################
class ThreadPM( threading.Thread ):

    def _printX( self, strn ):
        printT("PM:   " + strn )

    def __init__( self, send, rcvr ):
        super(ThreadPM,self).__init__()
        self.send    = send
        self.rcvr    = rcvr
        self.stopbit = False
        self.hitlist = ["45.0","135.0","225.0","315.0"]
        self._printX("*** thread starting")
        
    def run( self ):
        global pmRange
        random.shuffle( self.hitlist )
        for i in range(1, pmRange):
            self.cmd = "P: Go" + self.hitlist[ i % 4 ]
            self._printX   ( "snd = " + self.cmd )
            self.send.put ( self.cmd )
            self.resp = self.rcvr.getPM()
            if self.resp is None:
                self._printX("WARNING: no response")
            else:
                self._printX("rsp = " + self.resp)


        self._printX("*** thread ending")

######################################################################
# start up PLC serial port
if __name__ == "__main__":

    serport  = serial_init()    # defines plc

    send       = ThreadSend( serport )
    retryState = RetryState( send    )  # shared by send/rcvr
    rcvr       = ThreadRcvr( serport )
    send.start()
    rcvr.start()

    send.put( "C: Reset" )
    mess = rcvr.getC()

    pm = ThreadPM( send, rcvr )
    pm.start()

    gm = ThreadGM( send, rcvr )
    gm.start()

    ##################################################
    ### ALL threads are running now :)

    pm.join()
    gm.join()

    printT("Sending stop to send")
    send.put("G: Stop")

    send.stop()
    send.join()
    
    printT("Sending stop to rcvr")
    rcvr.stop()

    printT("Waiting for rcvr to join()")
    rcvr.join()
