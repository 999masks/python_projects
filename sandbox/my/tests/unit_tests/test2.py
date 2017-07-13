#!/usr/bin/python3

import time
import os.path
import sys
import random
import threading
import copy
import re

########################################
class StoppableThread( threading.Thread ):
    def __init__( self, name, delay ):
        super(StoppableThread, self).__init__()
        self.name  = name
        self.delay = delay
        self.stopped = True
        print ("Starting " + self.name)

    def stop( self ):
        self.stopped = True

    def isStopped( self ):
        return self.stopped 

    def run( self ):
        self.stopped = False

########################################
class TestThread( StoppableThread ):
    def __init__( self, name, delay ):
        super(TestThread, self).__init__( name, delay )

    def run( self ):
        super(TestThread,self).run() # run init
        for i in range(0,10):
            if super(TestThread,self).isStopped():
                print ( ("Brk %02d: %s") % (i, self.name) )
                return
            else:
                print ( ("Run %02d: %s") % (i, self.name) )
            time.sleep(self.delay)


t1 = TestThread("One",0.5)
t2 = TestThread("Two",0.33)
t3 = TestThread("Three",0.42)

t1.start()
t2.start()
t3.start()

time.sleep(2)
t2.stop()

t1.join()
t2.join()
t3.join()
