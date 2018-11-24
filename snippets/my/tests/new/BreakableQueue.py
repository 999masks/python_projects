from Queue import *
# import time

class QueueStop(Exception):
    """Break out of queue wait requested"""
    pass

class QueueTimeout(Exception):
    """break out of queue wait requested"""
    pass

class BreakableQueue:
    def __init__( self ):
        # super(BreakableQueue,self).__init__()
        self.q       = Queue()
        self.timeMax = 120 * 10
        self.stopbit = False

    def setTimeout( self, seconds ):
        self.timeMax = seconds * 10

    def stop( self ):
        self.stopbit = True

    def get( self ):
        # how long should max wait time be?
        try:
            for i in range(1,5*12): # 5 minutes
                return self.q.get( timeout=5 )

        except:
            if self.stopbit:
                print("DBG: raise QueueStop")
                raise QueueStop

    def put( self, entry ):
        self.q.put( entry )
        
