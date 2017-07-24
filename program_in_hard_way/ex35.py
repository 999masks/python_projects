from sys import exit

def gold_room():
    print "This room is fool of gold. How much do you take?"

    next =raw_input("> ")
    if "o" in next or "1" in next:
        how_much = int(next)
    else:
        dead("Man, you lear to type number.")

    if how_much < 50:
        print "Nice, you're not greedy, you win!"
        exit()
    else:
        dead("You greedy bastard!")

def bear_room():
    print "Ther is a bear here. \nThe bear has a bunch of honey. \nThe fat bear is in front of another door"
    print "How are you going to move the bear?"
    bear_moved = False

    while True:
        next = raw_input("> ")
        if next == "take honey":
            dead("The bear looks at you the slaps your face off.")
        elif next == "taunt bear" and not bear_moved:
            print "The bear has moved from the door. You can go through it now."
            bear_moved = True
        elif next == "Taunt bear" and bear_moved:
            dead("The bead gets pissed off and chews your led off.")
        elif next == "Open door" and bear_moved:
            gold_room()
        else:
            print "I got no idea what that means"

def cthulhu_room():
    print "Here you can see the great evil Cthulu."
    print "He, it whateve stares at youy and you go insane"
    print "Do you flee for your life or eat  your head?"

    next = raw_input("> ")

    if "flee" in next:
        start()
    elif "head" in next:
        dead("Welln that was tasty!")
    else:
        cthulhu_room()

def dead(why):
    print why, "Good job!"
    exit(0)

def start():
    print "You are in dark room"
    print "There is a door to your right and left"
    print "Which one do you take?"

    next = raw_input("> ")

    if next == "left":
        bear_room()
    elif next == "right":
        cthulhu_room()
    else:
        dead("You stumble around the room until you starve")

start()






