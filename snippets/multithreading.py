import threading
import  time

class threadrunner(threading.Thread):
    def __init__(self, name = "Test thread"):
        self._stopevent = threading.Event()
        self._sleepperioud = 4.0
        threading.Thread.__init__(self, name = name)
    def run(self):
        "main control loop"
        print "%s starts"% (self.getName(),)
        count = 0

        while True:
            print "second while"
            time.sleep(3)

        while not self._stopevent.isSet():
            count = 0
            print "looop %d "% (count,)
            self._stopevent.wait(self._sleepperioud)
        print "%s ends" % (self.getName(),)
    def join (self, timeout =None):
        """ Stop the thereads and wait fot it end.  """
        self._stopevent.set()
        threading.Thread.join(self, timeout)


if __name__ == "__main__":
    testthread = threadrunner()
    testthread.start()
    import time
    time.sleep(5.0)
    testthread.join()