###### Power measurement tes automator                                      ######
###### V0.11                                                                ######
###### Chanages:                                                            ######
###### 0.15 edited "IF" clauses to determine which devieces will cpature    ######
###### Author Mamo                                                          ######

import re
import sys
import time
import pyvisa
from matplotlib import pyplot
from collections import defaultdict
from adbandroid import adb_android, var
import visa
import time
import thread

from Tkinter import Frame, Button
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
matplotlib.use("TkAgg")
import Tkinter as tk

# TODO verify chain function calls, invokes
# TODO implement status code reading to indicate that command succes or not
# TODO degugging
# TODO add logging and timestasmp
# TODO lover all config string to make case insesnsitive
# TODO do plotting after done
# TODO add gui


#from Tkinter import Tk, Label, Button

############## GUI code ###########################

class measure_gui(Frame):
    res_data_set = []
    cycle_list = []

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.but_run = Button(master, text="Run", command=main)
        self.but_run.pack()
        self.but_start = Button(master, text="Start plot", command=self.start_plotting)
        self.but_start.pack()
        self.but_reset = Button(master, text="Reset", command=self.reset)
        self.but_reset.pack()
        self.but_show = Button(master, text="Show plot", command=self.show_canvas)
        self.but_show.pack()

    def start_plotting(self):
        f = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        a.plot(self.cycle_list, self.res_data_set)
        canvas = FigureCanvasTkAgg(f, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_canvas(self):
        print "nothing"

    def reset(self, canvas):
        self.cycle_list = []
        self.res_data_set = []
        self.canvas






'''
user_sel_1 =raw_input("Please choose, how you want to setup the test, Press 1 for interactive, or 2 to use config file ")

if user_sel_1 == "1":
    print ("You have choosen interactive mode ")
    phy = ("What typen of connection we are using ? ")
    if "USB" in phy:
        phy = "USB"
    elif "LAN" in phy:
        phy = "LAN"
    elif "GPIB" in phy:
        phy = "GBIP"
    else:
        print "That connection type cannot be identified"
    #go to this way

if user_sel_1 == "2":
    print ("You have choosen to use config file ")
    config_file_name = raw_input("Please choose config file ")


command_set_dict ={'CONN_TYPE': {'CT_value': 'TCPIP'}, 'MEAUSUREMNT_TYPE': {'MT_value': 'voltage'},\
                   'MEASURING_INSTRUMET': {'MI_IP_value': '10.0.100.27', 'MI_value': 'DMM775'}, \
                   'CAPTURE_TYPE': {'CT_value_flash_led': '1', 'CT_value_module': 'ALL', \
                    'CT_value_keep_files': 'YES'}, 'TEST_TYPE': {'3TT_value': 'soon', \
                    '2TT_value': 'w_flash', '1TT_value': 'capture_all'}, 'TEST_CYCLE': {'TC_value': 'contitious'}}
'''

# reading entire config file intead of line by line, to separate config blocks

def read_configurations(config_file_name="config.txt"):
    """
    :param config_file_name: is file with defined configuretions
    :return: nested dictianary with all parsed comamnds/values
    """
    # TODO issue with parsing flash command
    #seen issue where eror accesisng dictionary which not exist
    config_set =defaultdict(dict)
    config_file_data = open(config_file_name, "r").read()
    config_data_list = config_file_data.split()

    ### it scans all item from confg list until gets the end of config block, as soon as het the end record value in to dictionary
    for words in config_data_list:
        if re.search(r"#\*(.+?)\*#", words):
            match_conf_header = re.search("#{1}\*(.+?)\*#{1}?", words).group(1)

        if re.search(r"#-\*.+", words, re.M | re.I):
            match_conf_argument = re.search(r"#-\*(.+)=", words, re.M | re.I).group(1)
            match_conf_arg_value = re.search(r"=(.+)\*-#", words, re.M | re.I).group(1)

        if re.search(r"\*-#", words, re.M | re.I):
            config_set[match_conf_header][match_conf_argument]=match_conf_arg_value

    return (dict(config_set))

class mi_device():
    def _init_(self, command_set_dict):
        self.command_set_dict = command_set_dict
        self.mi_device = command_set_dict["MEASURING_INSTRUMET"]["MI_model"]
        self.phy_con = command_set_dict["CONN_TYPE"]["CT_value"]

    def mi_resource_finder(self, command_set_dict):
        """
        this will find any visa resources avaliable in local network conections
        utilized VISA libraries, also Keitley isntrument management tool
        :param command_set_dict:
        :return: device object
        """
        # TODO create device class
        # TODO add device IP ping routine, if TCPIP selected
        # TODO add connection type under measuring instrument config block
        mi_device = command_set_dict["MEASURING_INSTRUMET"]["MI_model"]


        if "sim" in mi_device:
            resources = pyvisa.ResourceManager("@sim")
        else:
            resources = pyvisa.ResourceManager()
        res_list =  resources.list_resources()
        print  "mi device is", (mi_device).upper(), ". Physical connection is:", self.phy_con

        if "DMM775" ==  mi_device:
            print "Kithley was found in confguration"
        elif mi_device == "simulator":
            print "We got virtual device"
        if mi_device:
            if "TCPIP" in self.phy_con:
                    for item in res_list:
                        if self.phy_con in item:
                            res_loc = res_list.index(item)
        else:
            print ("Error. Measuring instrument was not recognized")

        choosen_res = res_list[res_loc]
        #print ("Instrument %s and %s connetion will be used." % (mi_device, choosen_res))
        print ("Trying to connect...")

        try:
            mi_device = resources.open_resource(choosen_res)
            print "Resource got open"
            time.sleep(1)
            print "Resetting the instrument"
            mi_device.write("*RST")
            print "Testing the instrument, beeping.."
            #mi_device.write(":SYSTem:BEEPer 500, 1")
            return mi_device
        except:
            sys.exit("Measuring instrument is offline or command is wrong") # change to actual mi_device

    def mi_command_sender(self, mi_device, mi_command):
        # TODO implemenmt execution by time and cycle
        if mi_command in "power":
            # print "mi device", mi_device
            mi_device.write(("TRACe:MAKE '%s', 10000") % mi_command)
            time.sleep(1)
            cur_val = mi_device.query(("MEAS:DIG:VOLT? '%s'") % mi_command)
            cur_val = float(cur_val) / 1000000  # Need more polished integers
            mi_device.write("*RST")
        elif mi_command in "current":
            mi_device.write(("TRACe:MAKE '%s', 10000") % mi_command)
            time.sleep(1)
            cur_val = mi_device.query(("MEAS:DIG:CURR? '%s'") % mi_command)
            cur_val = float(cur_val) / 1000000  # Need more polished integers
            mi_device.write("*RST")
            # mi_device.query(":COUN %d"%cycle)
            # mi_device.query(":READ 'voltMeasBuffer_1'\n")
            # meas_data.append(mi_device.query(":TRAC:DATA? 1, 10, 'voltMeasBuffer'"))
            # time.sleep(3)
            # print "voltage buffer", votage_biuffer
        else:
            # raise
            print "MI Command was not recognized"

        return cur_val




def initialize_adb_device(command_set_dict):
    # TODO send ADB command explicitly to L16 by adb -s 'device name'
    devices_l = []
    try:
        #adbandroid.stop_server()
        adb_android.start_server()
        raw_dev_list = adb_android.devices()[1]
        dev_list = raw_dev_list.split("\n")
        for devs in dev_list[1:]:
            if len(devs.split("\t")[0])>3:
                devices_l.append(devs.split("\t")[0])
        #print "Found this devices: ", devices_l

        if len(devices_l) == 1:
            #TODO add other type of devices
            for devices in devices_l:
                if command_set_dict["DUT"]["DUT_value"] == "L16":
                    if "lfc" in devices.lower():
                        adb_device_obj = devices
                        #print "l16 selected, ID:", adb_device_obj
                elif command_set_dict["DUT"]["DUT_value"] == "HMD":
                    print "Not immplemented yet"
                elif command_set_dict["DUT"]["DUT_value"] == "emulator-5554":
                    if "emulator" in devices.lower():
                        adb_device_obj = devices
                        print "emulator was selected, ID:", adb_device_obj


        elif len(devices_l) > 1:
            print ("Error. More than one ADB devices are conected.")
            thread.interrupt_main()


        return adb_device_obj

    except:
        #pass
        sys.exit("Error while initializing an ADB device. Exiting...")





def interactive_command_send_reciver(mi_device):
    while True:
        read_write = raw_input("DO you want read or write to MI? ")
        if read_write.lower() in "read":
            command = raw_input("What you wont to send to read back ? ")
            print mi_device.read(command)
        elif read_write.lower() in "write":
            command = raw_input("What you wont to send to write ? ")
            print mi_device.write(command)





def adb_commandset_former(adb_command_set, adb_device):
    """
    :param adb_device: device object
    :return: cap_command, fi_command, keep_files
    """
    # TODO add option if user want to keep captured images
    # command set data structure -('CAPTURE_TYPE', {'CAP_value_module': 'ALL', 'CAP_value_flash': 'ON', 'CAP_value_type'\
    # : 'SINGLE', 'CAP_value_torch': 'ON'})
    # implement lcc check in /data/ directory

    if adb_device and "LFC" in adb_device:
        buid_info = str(adb_android.shell("getprop ro.build.version.incremental")[1]).split()
        if "c" in buid_info[0].lower():
            #first of copy lcc from /sys/etc/ to /data
            #change lcc permission
            print "Copying lcc binary to desired location"
            if not "denied" in str(adb_android.shell("cp /etc/lcc /data/; chmod 777 /data/lcc")):
                 print "LCC successfully copied"
            else:
                print "Error: Unable to copy LCC binary to desired location"
            adb_commands = adb_command_set["CAPTURE_TYPE"]
            #print "Got this", adb_commands, "sets of commands"
            for ct_item in adb_commands.items():
                if "CT_value_flash_led" in ct_item[0]:
                    if ct_item[1]=="2":
                        torch =True
                        print "Torch will be on. Switch possition: ", ct_item[1]
                        fl_command = "lcc -m 0 -s 0 -w -p 00 00 54 02 02 00 00 00 00"
                    elif ct_item[1]=="1":
                        print "Flash will be on. Switch possition", ct_item[1]
                        fl_command = "lcc -m 0 -s 0 -w -p 00 00 54 02 31 DC 05 DC 05 0A 00"
                    else:
                        fl_command = ""
                        print "Flash LED wil not be used", ct_item[1]
                if "CT_value_module" in ct_item[0]:
                    if ct_item[1] == "ALL":
                        cap_command = "lcc -m 0 -s 0 -f 1 01 00 00 11 21 00 -e 40000000 -g 2.0 -R 4160,3120"
                    elif ct_item[1] == "AB":
                        cap_command = "lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000"
                    elif ct_item[1] == "BC":
                        cap_command = "lcc -m 0 -s 0 -f 1 C0 FF 01 11 21 00 -e 40000000 -g 2.0 -R 4160,3120"
                    elif ct_item[1] == "A":
                        cap_command = "/lcc -m 0 -s 0 -f 1 3E 00 00 11 21 00 -e 40000000 -g 2.0 -R 4160,3120"

                # TODO add other capture_LCC combinations
                # TODO add ccb reboot, off options
                if "CT_value_keep_files" in ct_item[0]:
                    if "YES" in ct_item[1]:
                        keep_files= True
                        print "We will keep the files"
        elif "w" in buid_info[0].lower():
            sys.exit("Device software packages not capatible to ruin this test")
        else:
            sys.exit("unknown error")
        print "We will use %s module(s) for capture_LCC" % (adb_command_set["CAPTURE_TYPE"]["CT_value_module"])
        return(cap_command, fl_command, keep_files)

    elif adb_device and "emulator" in adb_device:
        print adb_device

    else:

        sys.exit("Cannot find L16 ADB device. Exiting...")


def plotting(iteration, values, mi_command, build_info =""):
    pyplot.plot(iteration,values, "o-")
    pyplot.ylabel(("%s"%mi_command))
    pyplot.xlabel("Iterations")
    if len(build_info)>1:
        pyplot.title(("Cyclic %s measuremnt, build version:%s"%(mi_command,build_info)))
    else:
        pyplot.title("Cyclic %s measuremnt, build version:%s" % mi_command)
    return pyplot



def main():
    global res_data_set
    global cycle_list
    command_set_dict = read_configurations()
    # Measurement device initialization
    try:
        mi_device = mi_device.mi_resource_finder(command_set_dict)
        print "Measurement instrument name is: ", mi_device
    except:
        #raise
        mi_device.close()
        sys.exit("%s measuring instrument was not found, exiting ..."%(command_set_dict["MEASURING_INSTRUMET"]["MI_model"]))

    mi_command = command_set_dict["MEAUSUREMNT_TYPE"]["MT_value"]
    print "Measurement command is: ", mi_command

    # ADB device initialization
    try:
        adb_device = initialize_adb_device(command_set_dict)
        print "DUT name is: ", adb_device
    except:
        raise
        mi_device.close()
        sys.exit("Cannot find any L16 connected to host, exiting..")

    number_of_cycles = command_set_dict["TEST_CYCLE"]["TC_value"]
    print "We will run test %s times"%number_of_cycles

    # ADB command set generation
    cap_command, fl_command, keep_files = adb_commandset_former(command_set_dict, adb_device)
    #print "Capture command is %s, flash parameter %s, keep files? %s"%(cap_command, fl_command, keep_files)

    # Starting cycle here:
    print "All set, starting measurement."
    if command_set_dict["DUT"]["DUT_build_info"] == "YES":
        print "Getting build info"
        build_info = str((adb_android.shell("getprop ro.build.version.incremental")[1]).split())
        print build_info
    if len(fl_command) > 0:
        adb_android.shell("/data/%s" % fl_command)
    if fl_command == 2:
        print "Turning toprch on"
        adb_android.shell("/data/%s" % fl_command)

    for i in range(1,int(number_of_cycles)+1):
        print "Runing cycle number %d" % i
        if fl_command == "1":
            print "Turning flash will be used during capture_LCC"
            adb_android.shell("/data/%s" % fl_command)
        adb_android.shell("/data/%s" % cap_command)
        cur_res = mi_command_sender(mi_device, mi_command)
        #print "Current value", cur_res
        cur_res = (1000000*float(('{0:.8f}'.format(cur_res))))
        measure_gui.res_data_set.append(cur_res)
        measure_gui.cycle_list.append(i)
        mi_device.write("*RST")

    mi_device.close()
    #plotting(cycle_list, res_data_set, mi_command, build_info)
    #pyplot.show()
    return "Measured values", res_data_set




#read_configurations("config.txt")
#initialize_adb_device()
#print command_set_finder("CAPTURE_TYPE", read_configurations(config_file_name))
#print adb_commandset_former(initialize_adb_device())
#for i in range(5):
    #print mi_command_sender()
    #adb_commandset_former(initialize_adb_device(), "CAPTURE_TYPE")
#    pass
#time.sleep(5)
#mi_device.close()
#print "device got closed"
#mi_command_sender()
# for i in range(1, 10):
#adb_commandset_former(adb_device)
#     print "Command is %d is runnnig"%i
#     time.sleep(1)
# for mi in range(1,5):
#     mi_command_sender(mi_resource_finder())

#my_dev =

if __name__== "__main__":
    #print "Tkinter will start"
    xxx= measure_gui().mainloop()

