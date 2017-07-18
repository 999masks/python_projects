import re
import time
from collections import defaultdict

import pyvisa

from keithley.adb_android.adb_android import adb_android

#TODO implement status code reading to indicate that command succes or not
#TODO degugging
#TODO add logging and timestasmp
#TODO lover all config string to make case insesnsitive
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

# decided to read entire config file intead of line by line, because i would likr to separate config blocks
def read_configurations(config_file_name="config.txt"):
    config_set =defaultdict(dict)
    config_file_data = open(config_file_name, "r").read()
    #print "config file data", config_file_data
    config_data_list = config_file_data.split()
    #print "confog data list", config_data_list

    ### it scans all item from confg list until gets the end of config block, as soon as het the end record value in to dictionary
    for words in config_data_list:
        if re.search(r"#\*(.+?)\*#", words):
            match_conf_header = re.search("#{1}\*(.+?)\*#{1}?", words).group(1)
            #print "header", match_conf_header
        if re.search(r"#-\*.+", words, re.M | re.I):
            match_conf_argument = re.search(r"#-\*(.+)=", words, re.M | re.I).group(1)
            match_conf_arg_value = re.search(r"=(.+)\*-#", words, re.M | re.I).group(1)

        if re.search(r"\*-#", words, re.M | re.I):

            #print "config_header", match_conf_header, "configuration argunment", match_conf_argument, "configur arg value", \
                #match_conf_arg_value
            #to fing when configuration block stops
            #print "configs", config_head, config_value
            #match_conf_argument[match_conf_argument]

            config_set[match_conf_header][match_conf_argument]=match_conf_arg_value


    #print "config set ", dict(config_set), type(config_set)
    return (dict(config_set))

command_set_dict = read_configurations()

def initialize_adb_device():

    try:
        adb_device = ""
        raw_dev_list = adb_android.devices()[1]
        dev_list = raw_dev_list.split("\n")
        #print "dev list", dev_list
        #print "command set dic", command_set_dict
        if len(dev_list) > 4:
            print "More than one ADB devices are exist"
        for devices in dev_list:
            if command_set_dict["DUT"]["DUT_value"] == "L16":
                if "lfc" in devices.lower():
                    adb_device = devices.split()[0]
                    print "l16 selected, ID:", adb_device
            elif command_set_dict["DUT"]["DUT_value"] == "HMD":
                print "NOt immplemented yet"


        #global adb_device
        return adb_device
    except:
        print "NO L16 CAMERA WAS FOUND"

def command_set_finder(config_group):
    """
    :param config_group: is basically cnonfiguration header, EX: TEST_TYPE
    :param command_set_dict: pass command set dictioanry
    :return: dictionary with command header and options valuse
    """
    #parse command group from sets of command
    #command_set_dict = read_configurations()
    #print "config_group", config_group, "command_set_dict", command_set_dict
    for command_set in command_set_dict.items():
        #print "1, 2", conpowerfig_data[0], config_group
        if config_group in command_set[0]:
            #return "config data", command_set
            break #we found our command set

    return command_set

def mi_resource_finder():
    #TODO create device class
    #TODO add device IP ping routine, if TCPIP selected
    #resources = pyvisa.ResourceManager("@sim")
    resources= pyvisa.ResourceManager("@sim")
    res_list =  resources.list_resources()
    print "We got these resources avaliable", res_list
    mi_device = command_set_dict["MEASURING_INSTRUMET"]["MI_model"]
    phy_con = command_set_dict["CONN_TYPE"]["CT_value"]
    print  "mi device", mi_device, "phy con", phy_con
    if "DMM775" ==  mi_device:
        print "Kithley was found in confguration"
        if "TCPIP" in phy_con:
            for item in res_list:
                if phy_con in item:
                    res_loc = res_list.index(item)
    elif mi_device == "TCPIP": # testing
        print ("got here")
        if "TCPIP" == phy_con:
            for item in res_list:
                if phy_con in item:
                    res_loc = res_list.index(item)
    else:
        print ("No match")
    choosen_res = res_list[res_loc]
    print ("Instrument %s and %s connetion will be used." % (mi_device, choosen_res))
    print ("Trying to connect...")

    try:

        mi_device = resources.open_resource(choosen_res)
        print "Resourse got open"
        #print mi_device
        #print (mi_device.write(":MEASure:CURRent:AC?")), "mi_device", mi_device #_WORKS!
        # test command mi_dev.query(":SYSTem:BEEPer 500, 1")
        #print (mi_device.read()), "mi_device", mi_device            _WORKS!
        #interactive_command_send_reciver(mi_device)
        #print "checking ...", mi_device
        #global mi_device
        return mi_device
    except:
        print "Measuring device is offline or command is wrong" # change to actual mi_device
        #sys.exit()


mi_device = mi_resource_finder()

def interactive_command_send_reciver(mi_device):
    while True:
        read_write = raw_input("Do you want read or write to MI? ")
        if read_write.lower() in "read":
            command = raw_input("What you wont to send to read back ? ")
            print mi_device.read(command)
        elif read_write.lower() in "write":
            command = raw_input("What you wont to send to write ? ")
            print mi_device.write(command)

def mi_command_sender(command="voltage", cycle=1):
    # TODO implemenmt execution by time and cycle
    DC = True
    if command in "voltage":
        if DC:
            volt_data = []
            print "mi device", mi_device
            mi_device.write("*RST")# can be combined with next command
            print "Resseting instrument"
            time.sleep(1)
            mi_device.write("TRACe:MAKE 'voltMeasBuffer_1', 10000 \n")
            time.sleep(1)
            mi_device.write("SENSe:FUNCtion 'CURRent:AC'\n")
            time.sleep(2)
            #mi_device.query(":COUN %d"%cycle)
            mi_device.query('voltMeasBuffer_1?')
            # volt_data.append(mi_device.query(":TRAC:DATA? 1, 10, 'voltMeasBuffer'"))
            #time.sleep(3)
            #print "voltage buffer", votage_biuffer

        #print "result buffer", result




'''
class executor():
    def __init__(self, adb_device):
        self.initialize_adb_device()

    def reset_dev(self):
        executor.adb_device.write("*RST")
        adb_device = "v"
        return adb_device

    def MI_write_to_buffer(self):
        pass
    def MI_read_from_buffer(self):
        pass
    def masurement_routine(self):

        pass
    def current_masuremtn_routine(self):
        pass

'''






def adb_command_former(adb_device):
    """
    :param adb_device: device object
    :return: no returns

    """
    # add option if user want to keep captured images
    # command set data structure -('CAPTURE_TYPE', {'CAP_value_module': 'ALL', 'CAP_value_flash': 'ON', 'CAP_value_type'\
    # : 'SINGLE', 'CAP_value_torch': 'ON'})
    # implement lcc check in /data/ directory

    if adb_device:
        #first off compy lcc from /sys/etc/ to /data
        #change lcc permission
        adb_android.shell("cp /etc/lcc /data/; chmod 777 /data/lcc")
        print "Copying lcc binary to correct spot"
        adb_command_set = command_set_finder("CAPTURE_TYPE")
        print adb_command_set
        for ct_item in adb_command_set[1].items():
            print "CT_item", ct_item
            if ct_item[0] in 'CT_value_flash_led':
                if ct_item[1] == "1":
                    flash = True
                elif ct_item[1] == "2":
                    torch = True
                elif ct_item[1] == "3":
                    torch, flash = False
            if ct_item[0] in 'CAP_value_module':
                print "ct_item1", ct_item[1]
                if ct_item[1] in "ALL" and flash :
                    print "Capturing all with flash"
                    adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000")
                elif ct_item[1] in "ALL" and torch :
                    print "Capturing all with torch"
                    adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000")
                elif ct_item[1] in "ALL" and not torch and not flash:
                    print "Capturing all no flash"
                    adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000")
                print "command was send"

            else:
                if len(ct_item[1])> 1:
                    if ct_item[1] in "A,B" and flash: # fill the code instead of true
                        # put correct command for group execution
                        print "Capturing A,B with flash"
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] in "A,B" and torch: # fill the code instead of true
                        # put correct command for group execution
                        print "Capturing A,B with torch"
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] in "A,B": # No flash LED
                        # put correct command for group execution
                        print "Capturing A,B NO flash" #HERE
                        #TODO find out how torch woks, youmay need to turn torch on, before iteration starts
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    if ct_item[1] in "A,C" and flash: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] in "A,C" and torch: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] in "A,C": # No flash LED
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    if ct_item[1] in "B,C" and flash: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] in "B,C" and torch: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] in "B,C": # No flash LED
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    else:
                        print "Module group has not identified"
                else:
                    if ct_item[1] == "A" and flash: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "A" and torch: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "A": # No flash LED
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "B" and flash: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "B" and torch: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "B": # No flash LED
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "C" and flash: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "C" and torch: # fill the code instead of true
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")
                    elif ct_item[1] == "C": # No flash LED
                        # put correct command for group execution
                        adb_android.shell("cd data; ./lcc -m 0 -s 0 -f 1 FE 07 00 11 21 00 -R 4160,3120 -g 7.75\
                        -e 40000000")

    else:
        "Prind cannot find any ADB device"




# flash paranmetd torch, flash, no flash

def adb_excuter(adb_device, command_set):
    pass







#read_configurations("config.txt")
#initialize_adb_device()
#print command_set_finder("CAPTURE_TYPE", read_configurations(config_file_name))
#adb_commandset_former(initialize_adb_device(), "CAPTURE_TYPE")
mi_command_sender()
time.sleep(5)
mi_device.close()
print "device got closed"
#mi_command_sender()
# for i in range(1, 10):
#adb_commandset_former(adb_device)
#     print "Command is %d is runnnig"%i
#     time.sleep(1)
# for mi in range(1,5):
#     mi_command_sender(mi_resource_finder())

#my_dev =
