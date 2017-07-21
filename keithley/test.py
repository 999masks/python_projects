###### Power measurement tes automator                                      ######
###### V0.11                                                                ######
###### Chanages:                                                            ######
###### 0.11 edited "IF" clauses to determine which devieces will cpature    ######
###### Author Mamo                                                          ######

import re
import sys
import time
from scipy import pyplot
from collections import defaultdict
from adbandroid import adb_android, var

import pyvisa

from adbandroid import adb_android

#TODO verufy chain function calls, invokes

#TODO implement status code reading to indicate that command succes or not
#TODO degugging
#TODO add logging and timestasmp
#TODO lover all config string to make case insesnsitive
# TODO do plotting after done
# TODO add gui
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
    # TODO issue with parsing flash command
    #seen issue where eror accesisng dictionary which not exist
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

    return (dict(config_set))



def initialize_adb_device(command_set_dict):
    devices_l = []
    try:
        #adbandroid.stop_server()
        adb_android.start_server()
        raw_dev_list = adb_android.devices()[1]
        #print "Raw dev list", raw_dev_list
        dev_list = raw_dev_list.split("\n")
        #print "dev list", dev_list
        for devs in dev_list[1:]:
            if len(devs.split("\t")[0])>3:
                devices_l.append(devs.split("\t")[0])
        print "Found this devices: ", devices_l
        if len(devices_l) > 1:
            print "More than one ADB devices are exist"
        #TODO add other devices
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

        return adb_device_obj
    except:
        #raise
        sys.exit("NO ADB DEVICE WAS FOUND. Exiting...")


def mi_resource_finder(command_set_dict):
    # TODO create device class
    # TODO add device IP ping routine, if TCPIP selected

    if "sim" in command_set_dict["MEASURING_INSTRUMET"]["MI_model"]:
        resources = pyvisa.ResourceManager("@sim")
    else:
        resources = pyvisa.ResourceManager()
    res_list =  resources.list_resources()
    #print "We got these resources avaliable", res_list
    mi_device = command_set_dict["MEASURING_INSTRUMET"]["MI_model"]
    phy_con = command_set_dict["CONN_TYPE"]["CT_value"]
    print  "mi device is", (mi_device).upper(), ". Physical connection is:", phy_con
    if "DMM775" ==  mi_device:
        print "Kithley was found in confguration"
    elif mi_device == "simulator":
        print "We got virtual device"
    if mi_device:
        if "TCPIP" in phy_con:
                for item in res_list:
                    if phy_con in item:
                        res_loc = res_list.index(item)
    else:
        print ("measuring instrument was not recognized")

    choosen_res = res_list[res_loc]
    #print ("Instrument %s and %s connetion will be used." % (mi_device, choosen_res))
    print ("Trying to connect...")

    try:
        mi_device = resources.open_resource(choosen_res)
        print "Resource got open"
        time.sleep(1)
        print "Resetting the instrument"
        mi_device.write("*RST")

        #print mi_device
        #print (mi_device.write(":MEASure:CURRent:AC?")), "mi_device", mi_device #_WORKS!
        print "Testing instrument, beeping.."
        mi_device.write(":SYSTem:BEEPer 500, 1")
        #print (mi_device.read()), "mi_device", mi_device            _WORKS!
        #interactive_command_send_reciver(mi_device)
        #print "checking ...", mi_device
        #global mi_device
        return mi_device
    except:
        sys.exit("Measuring instrument is offline or command is wrong") # change to actual mi_device
        #sys.exit()

def interactive_command_send_reciver(mi_device):
    while True:
        read_write = raw_input("DO you want read or write to MI? ")
        if read_write.lower() in "read":
            command = raw_input("What you wont to send to read back ? ")
            print mi_device.read(command)
        elif read_write.lower() in "write":
            command = raw_input("What you wont to send to write ? ")
            print mi_device.write(command)


def mi_command_sender(mi_device, mi_command):
    # TODO implemenmt execution by time and cycle
    #DC curretrnmeasurement command
    # [SENSe:[1]]:FUNCtion[:ON]...
    #print "Testing beep.."
    #mi_device.write(":SYSTem:BEEPer 280, 0.5")
    if mi_command in "voltage":
        print "mi device", mi_device
        time.sleep(1)
        mi_device.write(("TRACe:MAKE '%s', 10000")%mi_command)
        time.sleep(1)
        cur_val = mi_device.query(("MEAS:DIG:VOLT? '%s'")%mi_command)
        cur_val = float(cur_val)/1000000
        mi_device.write("*RST")
        # mi_device.query(":COUN %d"%cycle)
        #mi_device.query(":READ 'voltMeasBuffer_1'\n")
        # meas_data.append(mi_device.query(":TRAC:DATA? 1, 10, 'voltMeasBuffer'"))
        #time.sleep(3)
        #print "voltage buffer", votage_biuffer

        #print "result buffer", result

    elif mi_command in "current":
        print "mi device", mi_device
        time.sleep(1)
        mi_device.write(("TRACe:MAKE '%s', 10000")%mi_command)
        time.sleep(1)
        cur_val = mi_device.query(("MEAS:DIG:CURR? '%s'")%mi_command)
        cur_val = float(cur_val)/1000000
        mi_device.write("*RST")


    return cur_val


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






def adb_commandset_former(adb_command_set, adb_device):

    #print "Got this command set", adb_command_set, adb_device
    """
    :param adb_device: device object
    :return: cap_command, fi_command, keep_files
    """
    # add option if user want to keep captured images
    # command set data structure -('CAPTURE_TYPE', {'CAP_value_module': 'ALL', 'CAP_value_flash': 'ON', 'CAP_value_type'\
    # : 'SINGLE', 'CAP_value_torch': 'ON'})
    # implement lcc check in /data/ directory

    if adb_device and "LFC" in adb_device:
        #first off compy lcc from /sys/etc/ to /data
        #change lcc permission
        print "Copying lcc binary to correct spot..."
        adb_android.shell("cp /etc/lcc /data/; chmod 777 /data/lcc")
        print "LCC successfully copied"
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

            # TODO add other capture combinations
            # TODO add ccb reboot, off options
            if "CT_value_keep_files" in ct_item[0]:
                if "YES" in ct_item[1]:
                    keep_files= True
                    print "We will keep the files"
        print "We will use %s module(s) for capture" % (adb_command_set["CAPTURE_TYPE"]["CT_value_module"])
        return(cap_command, fl_command, keep_files)

    else:
        raise
        mi_device.close()
        sys.exit("Cannot find L16 ADB device. Exiting...")


def main():

    command_set_dict = read_configurations()
    # print command_set_dict

    # Measuremetn device initialization
    try:
        mi_device = mi_resource_finder(command_set_dict)
        print "Measurement instrument name is: ", mi_device
    except:
        raise
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
        sys.exit("No ADB device found, exiting..")

    number_of_cycles = command_set_dict["TEST_CYCLE"]["TC_value"]
    print "We will run test %s times"%number_of_cycles

    # ADB command set generation
    cap_command, fl_command, keep_files = adb_commandset_former(command_set_dict, adb_device)
    print fl_command
    print "Capture command is %s, flash parameter %s, keep files? %s"%(cap_command, fl_command, keep_files)

    # Starting cycle here:
    print "All set, starting to measure."
    if len(fl_command) > 0:
        adb_android.shell("/data/%s" % fl_command)
    if fl_command == 2:
        print "Turning toprch on"
        adb_android.shell("/data/%s" % fl_command)
    res_data_set = []
    for i in range(int(number_of_cycles)):
        print "Runing cycle number %d" % i
        if fl_command == "1":
            print "Turning flash will be used during capture"
            adb_android.shell("/data/%s" % fl_command)
        adb_android.shell("/data/%s" % cap_command)
        #adb_android.shell("pwd")
        #time.sleep(1)
        #adb_android.shell(cap_command)
        cur_res = mi_command_sender(mi_device, mi_command)
        print "Current value", cur_res
        cur_res = (1000000*float(('{0:.8f}'.format(cur_res))))
        res_data_set.append(cur_res)
        mi_device.write("*RST")
    mi_device.close()
    return "Measured values", res_data_set

print main()


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

#if __name__== "main":
#    main()
