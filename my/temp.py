'''

import time

def printT ( strsg ):
    """print with timestamp"""
    print( time.ctime() + "  " + strsg )



printT("home")

'''

def hammingWeight(n):
    w=0
    assert n>=0, "hammingWeight of %d is infinite"%n
    while (n!=0):
        w += (n & 1)
        n //= 2
    return w

print hammingWeight(-1)


