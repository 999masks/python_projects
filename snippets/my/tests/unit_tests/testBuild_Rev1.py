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

def TestLight( unit, messOn, messOff, name ):
    try:
        print ("########################################")
        print (">> Turn on " + name)
        sendMess( unit + messOn )
        resp = getMess().rstrip()
        assert( resp == (unit + b'Ok') )
        question("  + Is light on now? (Y/n/q) : ")
        print ("<< Pass")
        
        print (">> Turn off " + name)
        sendMess( unit + messOff )
        resp = getMess().rstrip()
        assert( resp == (unit + b'Ok') )
        question("  + Is light off? (Y/n/q) : ")
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
def TestMotor( unit, strName ):
    
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
        sendMess( unit + b'Home' )
        resp = getMess().rstrip()
        assertClose( resp[2:], 0 )
        question("  + is the motor home now ? (Y/n/q) : ")

    def sendPos( pos, notes ):
        absPos = pos % 360
        print ("   ##########" )
        print ("   Find Position %d (abs=%d)" % (pos, absPos) )
        if notes != "":
            print ("  + " + notes,flush=True)
        sendMess( unit + b'Go' + bytes(str(pos),'ascii') )
        resp = getMess().rstrip()
        assertClose( resp[2:], pos % 360 )
        question("  + is the motor in the right place? (Y/n/q) : ")

    def sendCmd( cmd ):
        sendMess( cmd + b'\r' )
        getMess()
        

    try:
        status[strName] = "Fail"
        print ("########################################")
        print ( ">> Test Motor " + strName )

        ser.timeout  = 120           # two minute timeout
        
        if strName == "PM":
            sendCmd( b'P: ELOn' )
            sendHome( "Orange on left, Green on right of PM window" )
            sendPos( 45    , "You should see orange gel")
            sendPos( 90+45 , "You should see gray/light purple gel")
            sendPos( 180+45, "You should see blue gel")
            sendPos( -45   , "You should see green gel")
            sendPos( 90+45 , "You should see gray/light purple gel")
            sendPos( 270+45, "You should see green gel")
            sendCmd( b'P: ELOff' )

        else:
            sendCmd( b'G: LedFrontOn' )
            sendHome( "From Front, you see distortion pattern (checkerbox)" )
            sendPos( 45, "From back, you see color charts" )
            sendPos( 90+45, "From front, you should see color charts" )
            sendPos( 180, "From front, you should see mirror now" )
            sendPos( -90, "the mirror should be pointing straight to the front" )
            sendHome( "From Front, you see distortion pattern (checkerbox)" )
            sendCmd( b'G: LedFrontOff' )

        status[strName] = "Pass"

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
        sendMess( b'G: RevNumber' )

        # make sure the revision is at least 1.06
        resp1  = getMess().rstrip()
        resp   = resp1[3:]
        rev    = float(resp.decode("utf-8"))
        assert( 1.06 <= rev )

        print ("<< Pass")
        
        ################################################3
        # set config to be safe
        print ("Enter config #")
        print ("  0 => China box")
        print ("  1 => Palo Alto box")
        print ("  3 => Taiwan box")
        print ("  > ",end='')
        ver = input().rstrip()
        if   ver == '0': sendMess( b'P: Config0' )
        elif ver == '3': sendMess( b'P: Config3' )

        elif ver == '1': sendMess( b'P: Config1' )
        else:
            print ("Sorry, must be 0,1,2 for now")
            sys.exit()
        resp = getMess().rstrip()
        assert( resp == b'P: Ok')

        ################################################3        
        # PM tests
        if bTestLights:
            printHeader( "Test PM lights" )
            TestLight( b'P: ', b'ELOn', b'ELOff', "PM Light" )
            
        if bTestPM:
            TestMotor( b'P: ', "PM" )

        ################################################3
        # GM tests
        if bTestLights:
            printHeader( "Test GM Front lights" )
            TestLight( b'G: ', b'LedFrontOn',  b'LedFrontOff',  "LedFront" )
            TestLight( b'G: ', b'D65FrontOn',  b'D65FrontOff',  "D65Front" )
            TestLight( b'G: ', b'TL84FrontOn', b'TL84FrontOff', "TL84Front" )
            
            printHeader( "Test GM Back lights" )
            TestLight( b'G: ', b'LedBackOn',   b'LedBackOff',   "LedBack" )
            TestLight( b'G: ', b'D65BackOn',   b'D65BackOff',   "D65Back" )
            TestLight( b'G: ', b'TL84BackOn',  b'TL84BackOff',  "TL84Back" )
            
            printHeader ("Halogen lights (may take up to 15 seconds to turn on and off)")
            TestLight( b'G: ', b'HalogenFrontOn', b'HalogenFrontOff', "HalogenFront" )
            TestLight( b'G: ', b'HalogenBackOn',  b'HalogenBackOff',  "HalogenBack" )
            
        if bTestGM:
            TestMotor( b'G: ', "GM" )

        ##################################################
        # leds on the front panel
        if bTestLeds:
            printHeader ("Test the little red leds on the front panel (Below red power button)")
            TestLight( b'G: ', b'FpLedTopOn',    b'FpLedTopOff',    "FpLedTop" )
            TestLight( b'G: ', b'FpLedBottomOn', b'FpLedBottomOff', "FpLedBottom" )
        
        
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
            
