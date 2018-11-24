

def is_prime(x):
    prime = False
    for i in range(2,abs(x)):
        if x%i == 0:
            prime = False
            #print "it will divide to number %d"% i
            return ("number %d is %s prime number, will divide to %d"%(x, prime, i))
            break
        else:
            prime = True
            continue
    return ("number %d is %s prime number"% (x, prime))


for i in range(0, 1000):
    print is_prime(i)


