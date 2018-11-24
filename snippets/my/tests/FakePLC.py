#!/usr/bin/python2

import random
import threading
import Queue
import time

debug = False

def printT ( strg ):
    """print with timestamp"""
    print( time.ctime() + "  " + strg )

class PlcTimeout(Exception):
    """Readline timed out"""
    pass


class FakePLC( threading.Thread ):

    def printX( self, strn, force=False ):
        if (self.debugLevel >= 3) or force:
            printT("PLC:  " + strn)

    def __init__( self, dbgLevel ):
        super(FakePLC,self).__init__()
        self.outQ    = Queue.Queue()
        self.cmd     = [None,None,None]
        self.hitlist = [0, 1, 2]
        self.pos     = "<Empty>"
        self.stopbit = False
        self.cnt     = 0
        self.debugLevel = dbgLevel
        self.printX("thread starting")

    def _getIndex( self, command ):
        if command[0:2]   == "G:":
            return 0
        elif command[0:2] == "P:":
            return 1
        elif command[0:2] == "C:":
            return 2 
        return -1

    def stop( self ):
        self.stopbit = True

    def run( self ):
        # emulate delays of commands in to commands out
        while not self.stopbit:
            random.shuffle( self.hitlist )
            for i in self.hitlist:
                if self.cmd[i] is not None:
                    time.sleep( random.randrange(0,2) )
                    # noinspection PyTypeChecker
                    self.printX( "run cmd = " + self.cmd[i] )
                    self.tag     = self.cmd[i][0:2]
                    self.op      = self.cmd[i][3:].rstrip()

                    self.printX("run op = " + self.op)
                    
                    if self.op == "Reset":
                        time.sleep(2)
                        self.pos  = "<NoPosition>"
                        self.resp = "ResetDone"

                    elif self.op == "Stop":
                        time.sleep(1)
                        self.stopbit = True
                        self.resp = "Stop"

                    elif self.op == "Home":
                        self.pos  = "0.00"
                        self.resp = "0.00"

                    elif self.op[0:2] == "Go":
                        self.resp = self.op[2:].rstrip()
                        self.pos  = self.resp

                    elif self.op[0:3] == "Pos":
                        self.resp = self.pos

                    else:
                        self.resp = "Ok"

                    self.resp = self.tag + " " + self.resp

                    # corruption
                    if self.cnt == 5:
                        self.resp = "* " + self.tag + " " + self.resp
                        self.printX("run Resp = " + self.resp, force=True )

                    self.cnt = self.cnt + 1
                    self.printX("run Resp = " + self.resp )
                    self.cmd[i] = None
                    self.outQ.put( self.resp )
            
        # wait for output queue to empty
        while not self.outQ.empty():
            pass

    ##################################################
    # same as Serial
    def close( self ):
        pass

    def flushInput( self ):
        pass

    def write( self, bcommand ):
        self.command = bcommand.decode().rstrip()             # bString -> String

        inx = self._getIndex( self.command )
        if inx is None:
            self.printX("Badly formatted command dropped")
        elif self.cmd[inx] is not None:
            self.printX("Unit busy, dropping command:" + self.command)
        else:
            self.cmd[inx] = self.command

    def readline(self):
        for i in range(1,100):
            try:
                return self.outQ.get_nowait().encode() + "\r" # String -> bString
            except:
                time.sleep(0.1)

        return PlcTimeout

######################################################################
if __name__ == "__main__":

    plc = FakePLC(1)
    plc.start()

    printT   ( "C: Reset")
    plc.write(b'C: Reset\r' )
    printT   ( "    => " + plc.readline().decode())

    printT   ( "G: Home")
    plc.write(b'G: Home\r' )
    printT   ( "    => " + plc.readline().decode())
    
    printT   ( "P: Home")
    plc.write(b'P: Home\r' )
    printT   ( "    => " + plc.readline().decode())
    
    printT   ( "P: Go45.2")
    plc.write(b'P: Go45.2\r' )
    printT   ( "    => " + plc.readline().decode())
    
    printT   ( "P: Pos")
    plc.write(b'P: Pos\r' )
    printT   ( "    => " + plc.readline().decode())

    printT   ( "P: Go123.1")
    plc.write(b'P: Go123.1\r' )
    printT   ( "G: Go321")
    plc.write(b'G: Go321\r')
    printT   ( "    => " + plc.readline().decode())
    printT   ( "    => " + plc.readline().decode())

    plc.stop()
    plc.join()
