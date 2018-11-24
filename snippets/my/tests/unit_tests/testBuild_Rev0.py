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

def sendMess( mess ):
    ser.write( mess + b'\r' )
    print (("    %s Send %s") % (time.ctime(),mess))
    time.sleep(0.2)

def getMess():
    resp = ser.readline()
    print (("    %s Ack = %s") % (time.ctime(),resp.rstrip()) )
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
        sendMess( messOn )
        resp = getMess().rstrip()
        assert( resp == b'OK' )
        question("  + Is light on now? (y/<cr>/n/q) : ")
        print ("<< Pass")
        
        print (">> Turn off " + name)
        sendMess( messOff )
        resp = getMess().rstrip()
        assert( resp == b'OK' )
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
    homeMess = name + b'Home'
    posMess  = name
    strName  = str(name,'utf-8')
    
    def assertClose( resp, exp ):
        got = float(resp)
        ok  = False
        if abs ( got - exp ) < 1.0 :
            ok = True
        elif abs ( 360 + got - exp ) < 1.0 :
            ok = True
        elif abs ( got - (360 + exp) ) < 1.0 :
            ok = True

        if ok == False:
            print ("ERROR: got = %f, exp = %f" % (got, exp))
            raise TestOutOfRange

    def sendHome( notes ):
        print ("   ##########" )
        print ("   Find Home" )
        if notes != "":
            print ("  + " + notes,flush=True)
        sendMess( homeMess )
        resp = getMess().rstrip()
        assertClose( resp, 0 )
        question("  + is the motor home now ? (y/<cr>/n/q) : ")

    def sendPos( pos, notes ):
        absPos = pos % 360
        print ("   ##########" )
        print ("   Find Position %d (abs=%d)" % (pos, absPos) )
        if notes != "":
            print ("  + " + notes,flush=True)
        sendMess( posMess + bytes(str(pos),'ascii') )
        resp = getMess().rstrip()
        assertClose( resp, pos % 360 )
        question("  + is the motor in the right place? (y/<cr>/n/q) : ")

    def sendCmd( cmd ):
        sendMess( cmd + b'\r' )
        getMess()
        

    try:
        status[strName] = "Pass"
        print ("########################################")
        print ( ">> Test Motor " + strName )

        ser.timeout  = 120           # two minute timeout
        
        if name == b'PM':
            sendCmd( b'ELOn' )
            sendHome( "Orange on left, Green on right of PM window" )

            sendPos( 45    , "You should see orange gel")
            sendPos( 135   , "You should see light purple gel")
            sendPos( 225   , "You should see blue gel")
            sendPos( 315   , "You should see green gel")
            sendPos( 135   , "You should see light purple gel")
            sendPos( 315   , "You should see green gel")
            sendPos( 45    , "You should see orange gel")
            
            sendCmd( b'ELOff' )

        else:
            sendCmd( b'LedFrontOn' )
            sendHome( "From Front, you see checker box pattern" )
            sendPos( 45, "" )
            sendPos( 90+45, "You should see color charts now" )
            sendPos( 180, "You should see mirror now" )
            sendPos( -90, "" )
            sendHome( "From Front, you see checker box pattern" )
            sendCmd( b'LedFrontOff' )

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
        printHeader( "Check Revision Number")
        print (">> Test RevNumber")
        sendMess( b'RevNumber' )

        # make sure the rev is at least 27, but not 1.0+
        resp   = getMess().rstrip()
        rev    = float(resp.decode("utf-8"))
        assert( (0.27 <= rev) and (rev <= 0.99) )
        print ("<< Pass")
        
        ################################################3
        # set config to be safe
        print ("  0 => China box")
        print ("  1 => Palo Alto box")
        print ("  3 => Taiwan box")
        print ("  > ",end='')
        ver = input().rstrip()

        # new world order is config = 0
        if   ver == '0': sendMess( b'Config0' )
        
        # old pins (meaning halogens, etc)
        elif ver == '1': sendMess( b'Config1' )
        elif ver == '3': sendMess( b'Config3' )  # :NOTE: make sure this is right?

        else:
            print ("Sorry, must be 0,1,3 for now")
            sys.exit()

        resp = getMess().rstrip()
        assert( resp == b'OK')

        if bTestLights:
            ##################################################
            printHeader( "Test PM lights" )
            TestLight( b'ELOn', b'ELOff', "PM Light" )
            
            ##################################################
            printHeader( "Test GM Front lights" )
            TestLight( b'LedFrontOn',  b'LedFrontOff',  "LedFront" )
            TestLight( b'D65FrontOn',  b'D65FrontOff',  "D65Front" )
            TestLight( b'TL84FrontOn', b'TL84FrontOff', "TL84Front" )
            
            ##################################################
            printHeader( "Test GM Back lights" )
            TestLight( b'LedBackOn',   b'LedBackOff',   "LedBack" )
            TestLight( b'D65BackOn',   b'D65BackOff',   "D65Back" )
            TestLight( b'TL84BackOn',  b'TL84BackOff',  "TL84Back" )
            
            ##################################################
            printHeader ("Halogen lights (may take up to 15 seconds to turn on and off)")
            TestLight( b'HalogenFrontOn', b'HalogenFrontOff', "HalogenFront" )
            TestLight( b'HalogenBackOn',  b'HalogenBackOff',  "HalogenBack" )
            
        ##################################################
        if bTestLeds:
            printHeader ("Test the little red leds on the front panel (Below red power button)")
            TestLight( b'FpLedTopOn',    b'FpLedTopOff',    "FpLedTop" )
            TestLight( b'FpLedBottomOn', b'FpLedBottomOff', "FpLedBottom" )
        
        ##################################################
        if bTestPM:
            TestMotor( b'PM' )

        if bTestGM:
            TestMotor( b'GM' )
        
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
            
