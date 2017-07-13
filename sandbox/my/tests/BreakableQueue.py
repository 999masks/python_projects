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
        self.stopbit = False
        self.timeMax = int(180 / 12)  # 180 seconds in 5 second increments
        
    def setTimeout( self, seconds ):
        self.timeMax = int(seconds / 12)

    def stop( self ):
        self.stopbit = True

    def get( self ):
        # how long should max wait time be?

        for i in range(1,self.timeMax): # 2 minutes
            try:
                return self.q.get( timeout=5 )

            except Empty:
                if self.stopbit:
                    print("DBG: raise QueueStop")
                    raise QueueStop

        raise QueueTimeout


    def put( self, entry ):
        self.q.put( entry )
        
    
