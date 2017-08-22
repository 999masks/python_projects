import re
import sys
import time
import pyvisa
from matplotlib import pyplot
from collections import defaultdict
from adbandroid import adb_android, var
from subprocess import call

command_set_dic = {'CONN_TYPE': {'CT_value': 'TCPIP'}, 'MEAUSUREMNT_TYPE': {'MT_value': 'voltage'},\
                   'MEASURING_INSTRUMET': {'MI_IP_value': '10.0.100.27', 'MI_model': 'DMM775'}, \
                   'CAPTURE_TYPE': {'CT_value_flash_led': '1', 'CT_value_module': 'ALL', \
                    'CT_value_keep_files': 'YES'}, 'TEST_TYPE': {'3TT_value': 'soon', \
                    '2TT_value': 'w_flash', '1TT_value': 'capture_all'}, 'TEST_CYCLE': {'TC_value': 'contitious'}}

def mi_resource_finder(command_set):
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
    phy_con = command_set_dict["CONN_TYPE"]["CT_value"]

    if "sim" in mi_device:
        resources = pyvisa.ResourceManager("@sim")
    else:
        resources = pyvisa.ResourceManager()
    res_list =  resources.list_resources()
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
        print "Testing the instrument, beeping.."
        mi_device.write(":SYSTem:BEEPer 100, 1")
        return mi_device

    except:
        sys.exit("Measuring instrument is offline or command is wrong") # change to actual mi_device


def mi_command_sender(mi_device, mi_command):
    # TODO implemenmt execution by time and cycle
    if mi_command in "power":
        #print "mi device", mi_device
        mi_device.write(("TRACe:MAKE '%s', 10000")%mi_command)
        time.sleep(1)
        cur_val = mi_device.query(("MEAS:DIG:VOLT? '%s'")%mi_command)
        cur_val = float(cur_val)/1000000 #Need more polished integers
        mi_device.write("*RST")
    elif mi_command in "current":
        mi_device.write(("TRACe:MAKE '%s', 10000") % mi_command)
        time.sleep(1)
        #cur_val = mi_device.query(("MEAS:DIG:CURR? '%s'") % mi_command)
        mi_device.write("CURR:RANGE 10")
        cur_val = mi_device.query(("TRACe:STAT:MAXimum? '%s'")%mi_command)
        cur_val = float(cur_val)/ 1000000  # Need more polished integers
        #mi_device.write("*RST")
        # mi_device.query(":COUN %d"%cycle)
        #mi_device.query(":READ 'voltMeasBuffer_1'\n")
        # meas_data.append(mi_device.query(":TRAC:DATA? 1, 10, 'voltMeasBuffer'"))
        #time.sleep(3)
        #print "voltage buffer", votage_biuffer
    else:
        raise
        print "MI Command was not recognized"

    return cur_val


def main():
    midevice = mi_resource_finder(command_set_dict)
    mi_command_sender(midevice, "current")


kill_app




main()
