print "You enter a dark room with two doors. Do you gp trough door #1 or door #2?"

door = raw_input("> ")

if door == "1":
    print "There`a a giant bear eating cheesa cake. What do you do?"
    print "1. Take the cake."
    print "2. Scream at the bear."

    bear = raw_input("> ")

    if bear == "1":
        print "The bear eats your face off. Good job!"
    elif bear == "2":
        print "The bear eats your legs off. Good job!"
    else:
        print "Well, doing %s is probably better. Bear runs away." %bear

elif door == "2":
    print "You stat into the endless abysss ar Cthulu`s retina"
    print "1. Blueberries."
    print "2. Yelllow jacket clothespons. \n3. Understanding revolvers yelling meodies. "

    instantly = raw_input("> ")

    if instantly == '1' or instantly == "2":
        print "Your body survives powerer by mint of jello. Good job!"
    else:
        print "THe insanity rots your eyes into pool of muck. Good job!"

else:
    print "You stumble around and fall on knife and die. Good job!"
