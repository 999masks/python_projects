def add (a,b):
    print "Adding %d + %d" %(a,b)
    return a+b

def substract(a,b):
    print "Substracting %d - %d"%(a,b)
    return a-b

def multiply(a, b):
    print "Multiplying %d x %d" %(a,b)
    return a*b

def divide(a,b):
    print "Dividing %d to %d" %(a,b)
    return a/b
print "let's do some math with just functions!"


age = add(30,5)
height = substract(78,4)
weight = multiply(90, 2)
iq = divide(100, 2)

print "Age: %d, Height %d, Wieght: %d, IQ: %d " %(age, height, weight, iq)

#A puzzle for ectra creditm type it in anyway.

print "Here is a puzzle."

what = add(age, substract(height, multiply(weight, divide(iq,2))))

print "That's  becomes: ", what, "Can you do it by hand"