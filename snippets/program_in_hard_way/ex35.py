from sys import exit

def gold_room():
    print "This room is fool of gold. How much do you take?"

    choice =raw_input("> ")
    if "o" in choice or "1" in choice:
        how_much = int(choice)
    else:
        dead("Man, you lear to type number")

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
        choice = raw_input("> ")
        if choice == "take honey":
            dead("The bear looks at you the slaps your face off.")

