import visa
import time
from Tkinter import Tk, Label, Button
window = Tk()
label = Label(window, "Test result")
window.title = "Cyclic Test"
label.pack()
b_enter = Button(text="Start", command=main)

#TODO move to buttom of code
window.mainloop()
rs=visa.ResourceManager()
print rs.list_resources()

keithley = rs.open_resource("TCPIP0::10.0.100.137::inst0::INSTR")
print "REs open"
print "Testing beep.."
keithley.write(":SYSTem:BEEPer 100, 2")
#time.sleep(2)

def mi_command_sender(command, R):
    keithley.write("*RST")
    # TODO implemenmt execution by time and cycle
    #DC curretrnmeasurement command
    # [SENSe:[1]]:FUNCtion[:ON ]...

    if R:
        print "reading"
        sent = keithley.query(command)
    else:
        print "writing"
        sent = keithley.write(command)
        return sent

while True:
    try:
        raw_command = raw_input("PLease send the command..")
        command = raw_command.split("--")[0]
        if "R" in raw_command.split("--")[-1]:
            R = True
            mi_command_sender(command, R)
        elif "W" in raw_command.split("--")[-1]:
            R = False
            mi_command_sender(command, False)

        elif "EX" in raw_command.split("--")[-1]:
            break
    except:
        print"Something went wrong"


keithley.close()
print "Resourse got closed"