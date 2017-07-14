#!/usr/bin/python3

import time
import os.path
import serial
import random
import sys

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

def sendC( mess ):
    ser.write( b'C: ' + mess + b'\r' )
    print (("    %s Send 'C: %s''") % (time.ctime(),mess))
    time.sleep(0.2)

def sendPM( mess ):
    ser.write( b'P: ' + mess + b'\r' )
    print (("    %s Send 'P: %s'") % (time.ctime(),mess))
    time.sleep(0.2)

def sendGM( mess ):
    ser.write( b'G: ' + mess + b'\r' )
    print (("    %s Send 'G: %s'") % (time.ctime(),mess))
    time.sleep(0.2)

def getResp():
    resp = ser.readline().rstrip()
    print (("    %s Ack = %s") % (time.ctime(),resp) )
    return resp


######################################################################
class Error(Exception):
    pass

class TestQuit(Error):
    def __init__(self):
        self.message = "User selected Quit"

class TestFail(Error):
    def __init__(self):
        self.message = "User says test failed"

class TestOutOfRange(Error):
    def __init__(self):
        self.message = "Value was out of range"

######################################################################
def question(mess):
    print (mess,end='',flush=True)
    res = input().rstrip()
    if res == 'Y' or res == 'y' or res == '':
        return
    elif res == 'q' or res == 'Q':
        raise TestQuit
    else:
        raise TestFail

######################################################################
status = dict()

def TestLight( messOn, messOff, name ):
    try:
        print ("########################################")
        print (">> Turn on " + name)
        sendGM( messOn )
        resp = getResp()
        assert( resp == b'G: Ok' )
        question("  + Is light on now? (y/<cr>/n/q) : ")
        print ("<< Pass")
        
        print (">> Turn off " + name)
        sendGM( messOff )
        resp = getResp()
        assert( resp == b'G: Ok' )
        question("  + Is light off? (y/<cr>/n/q) : ")
        status[name] = "Pass"

    except TestFail:
        print ("<< fail raised")
        status[name] = "Fail"

    except TestQuit:
        status[name] = "Fail"
        raise TestQuit
        
    finally:
        print ("<< " + status[name])

######################################################################
def TestMotor( name ):
    homeMess = b'Home'
    posMess  = name
    strName  = str(name,'utf-8')
    
    def assertClose( resp, exp ):
        got = float(resp)
        ok  = False
        if abs ( got - exp ) < 0.21 :
            ok = True
        elif abs ( 360 + got - exp ) < 0.21 :
            ok = True
        elif abs ( got - (360 + exp) ) < 0.21 :
            ok = True

        if ok == False:
            print ("ERROR: got = %f, exp = %f" % (got, exp))
            raise TestOutOfRange

    def sendHome( notes ):
        print ("   ##########" )
        print ("   Find Home" )
        if notes != "":
            print ("  + " + notes,flush=True)
        sendGM( homeMess )
        resp = getResp()
        assertClose( resp[3:], 0 )
        # question("  + is the motor home now ? (y/<cr>/n/q) : ")

    def sendAndGetResp( cmd ):
        sendGM( cmd )
        return getResp()
        
    try:
        status[strName] = "Pass"
        print ("########################################")
        print ( ">> Test Motor " + strName )

        ser.timeout  = 120           # two minute timeout
        
        sendAndGetResp( b'LedFrontOn' )

        sendHome( "Go home" ) 
        time.sleep(0.5)

        random.seed(0);
        hitList = [0,180,45,135,225,315]
        
        count = 0
        for i in range(1,5):
            random.shuffle( hitList )  # random order
            
            for j in hitList:
                print ("################################")
                print (("  + Go to %d") % (j));
                cmd = b'Go' + bytes(str(j), 'utf-8')
                resp = sendAndGetResp( cmd )
                assertClose( resp[3:], j )
                
        j = 0
        print ("################################")
        print (("  + Go to %d") % (j));
        cmd = b'Go' + bytes(str(j), 'utf-8')
        resp = sendAndGetResp( cmd )
        assertClose( resp[3:], j )

    except TestFail:
        status[strName] = "Fail"

    except TestQuit:
        status[strName] = "Fail"
        raise TestQuit
        
    finally:
        ser.timeout  = 20
        print ("<< " + status[strName])



######################################################################
if __name__ == "__main__":

    bTestLights = True
    bTestLeds   = True
    bTestPM     = True
    bTestGM     = True

    def printHeader( mess ):
        print( "\n" )
        print( "######################################################################" )
        print( "######################################################################" )
        print( "\n" + mess + "\n" )

    ######################################################################
    # test PM
    try:
        printHeader( "Reset" )
        print (">> Send Reset")
        sendC( b'Reset' );
        resp   = getResp()
        assert( resp == b'C: Reset Done' );
        print ("<< Pass")

        ################################################3
        printHeader( "Check Revision Number")
        print (">> Test RevNumber")
        sendGM( b'RevNumber' )

        # make sure the rev is at least 27, but not 1.0+
        resp   = getResp()[3:]
        rev    = float(resp.decode("utf-8"))
        assert( (1.00 <= rev) and (rev <= 1.99) )
        print ("<< Pass")
        
        ################################################3
        # set config to be safe
        print ("  0 => China box")
        print ("  1 => Palo Alto box")
        print ("  3 => Taiwan box")
        print ("  > ",end='')
        ver = input().rstrip()

        # new world order is config = 0
        if   ver == '0': sendPM( b'Config0' )
        
        # old pins (meaning halogens, etc)
        elif ver == '1': sendPM( b'Config1' )
        elif ver == '3': sendPM( b'Config3' )  # :NOTE: make sure this is right?

        else:
            print ("Sorry, must be 0,1,3 for now")
            sys.exit()

        resp = getResp()
        assert( resp == b'P: Ok')

        TestMotor( b'G: ' )
        
    except TestQuit:
        print("User requested test quit")
        
    except:
        print("Error Raised:", sys.exc_info()[0])
        
    finally:
        ser.close()
        
    print ("########################################")
    print ("Test Summary")
    for key in status:
        print (key + " = " + status[key])
            
