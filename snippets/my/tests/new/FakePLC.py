#!/usr/bin/python2

import random
import threading
import Queue
import time

debug = True

def printT ( strg ):                    #  print function
    """print with timestamp"""
    print( time.ctime() + "  " + strg )

class FakeUnit( threading.Thread ):
    def __init__( self, tag,sleepHome,sleepGo ):
        super(FakeUnit,self).__init__()
        self.inQ  = Queue.Queue()
        self.outQ = Queue.Queue()
        self.stopbit = False
        self.tag = tag
        self.pos = "<Empty>"
        self.sleepHome = sleepHome
        self.sleepGo = sleepGo
        printT("FakeUnit " + tag.decode() + ": starting")

    def printX( self, strg ):
        printT(self.tag + ": " + strg)

    def stop( self ):
        self.stopbit = True

    def put( self, command ): #?
        self.inQ.put( command )

    def get( self, cmd ):
        return self.tag + ": "+ self.outQ.get_nowait( cmd )
    
    def notBusy( self ):
        return self.inQ.empty() and self.outQ.empty()

    def run( self ):
        while not self.stopbit:
            try:
                self.cmd = self.inQ.get_nowait()
                try:
                    self.printX("run cmd = " + self.cmd)
                except:
                    self.printX("EXCEPT")
                    print(self.cmd)

                if self.op == "Stop":
                    time.sleep(1)
                    self.stopbit = True
                    self.resp = "Stop"
                    
                elif self.op == "Home":
                    self.pos = "0.00"
                    time.sleep(sleepHome)
                    self.resp = self.pos 
                    
                elif self.op[0:2] == "Go":
                    self.pos = self.op[2:].rstrip()
                    time.sleep(sleepGo)
                    self.resp = self.pos 
                    
                elif self.op[0:3] == "Pos":
                    self.resp = self.pos
                    
                else:
                    self.resp = "Ok"

                self.printX("run resp = " + self.resp)
                self.outQ.put ( self.resp )

            except:
                time.sleep(0.2)
                

class FakePLC( threading.Thread ):
    def printX( self, strn ):
        if not debug:
            return
        if type(strn) == type(b'123'):
            printT("PLC:  " + strn.decode())
        else:
            printT("PLC:  " + strn)

    def __init__( self ):
        super(FakePLC,self).__init__()
        self.gm      = FakeUnit("G",7,3)
        self.pm      = FakeUnit("P",5,2)
        self.c       = FakeUnit("C",1,1)
        
        self.outQ    = Queue.Queue()
        self.stopbit = False
        self.gm.start()
        self.pm.start()
        self.c.start()
        self.printX("thread(s) starting")

    def stop( self ):
        self.stopbit = True

    def run( self ):                                # this method is overrides thread method...M
        # pull things out units and put them in outQ
        while not self.stopbit:
            self.printX("run loop")
            try:
                self.res = self.gm.get()
                self.printX("run self.pm = " + self.res)
                self.outQ.put(res)
            except:
                pass

            try:
                self.res = self.pm.get()
                self.printX("run self.pm = " + self.res)
                self.outQ.put(res)
            except:
                pass

            try:
                self.res = self.c.get()
                self.printX("run self.c = " + self.res)
                self.outQ.put(res)
            except:
                pass

            time.sleep(0.3)

    ##################################################
    # same as Serial
    def close( self ):
        pass

    def flushInput( self ):
        pass

    def write( self, command ):
        self.tag     = command[0:3].decode().rstrip()
        self.op      = command[3:].decode().rstrip()

        if (self.tag == "G:"):
            if self.gm.notBusy():
                self.printX("Write: " + self.tag + " " + self.op)
                self.gm.put(self.op)

        elif (self.tag == "P:"):
            if self.pm.notBusy():
                self.printX("Write: " + self.tag + " " + self.op)
                self.pm.put(self.op)

        elif (self.tag == b"C:"):
            if self.c.notBusy():
                self.printX("Write: " + self.tag + " " + self.op)
                self.c.put(self.op)

        else:
            self.printX("Badly formatted command dropped")
            exit()

    def readline(self):
        for i in range(1,100):
            try:
                self.resp = self.outQ.get_nowait().encode()
                return self.resp
            except:
                time.sleep(0.1)

        return None

######################################################################
if __name__ == "__main__":


        plc = FakePLC()
        plc.start()

        printT     ("C: Reset")
        plc.write( b'C: Reset\r' )
        printT ("    => " + plc.readline().decode())

        printT     ("G: Home")
        plc.write( b'G: Home\r' )
        printT ("    => " + plc.readline().decode())

        printT     ("P: Home")
        plc.write( b'P: Home\r' )
        printT ("    => " + plc.readline().decode())

        printT     ("P: Go45.2")
        plc.write( b'P: Go45.2\r' )
        printT ("    => " + plc.readline().decode())

        printT     ("P: Pos")
        plc.write( b'P: Pos\r' )
        printT ("    => " + plc.readline().decode())

        printT     ("P: Go123.1")
        plc.write( b'P: Go123.1\r' )
        printT     ("G: Go321")
        plc.write( b'G: Go321\r' )
        printT ("    => " + plc.readline().decode())
        printT ("    => " + plc.readline().decode())

        #plc.stop()
        #plc.join()
