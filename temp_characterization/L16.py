##############################################
# Ligh L16 main class
# current version V0.5
# created by Mamo 11/01/2017
# Light.co
# ..............
# ..............
# ..............
# Changelog
#  V 0.1 base version
#  V 0.2 ...........
#  V 0.3
#  V 0.4
## V 0.5 added miltiple unit conection functionality

from adbandroid import adb_android
import re
import sys
import subprocess

import time
from time import strftime, localtime

import struct



# TODO read temp sensors
# TODO each function shuld return used time on cycles Done
# LCC captures

#debug = True
debug = False
MP_firmware = True

class L16:
    D = 60  # for User Build 200 and later
    T = 400  # Choose time in ms to swipe D pixels (affects consistency of zoom amount)
    X = 1920 / 2  # Center horizontal touchscreen pixel location
    Y = 1080 / 2  # Center vertical touchscreen pixel location
    SS_button_x = '1750'
    SS_button_y = '750'
    reset = ' -1000'
    ISO_button_x = '1750'
    ISO_button_y = '300'
    adb_device = None


    # def __init__(self):
    #     if not debug:
    #         pass
    #     else:
    #         self.dev_list = []
    #         self.adb_obj = adb_android
    #         self.adb_obj.start_server()
    #         self.connect()
    #         self.startLightapp()
    #         #uncomment if you need to use LCC for capture_LCC
    #         # print "Trying to copy LCC binary to /data/ dir\r "
    #         # adb_android.shell("cp /etc/lcc /data/; chmod 777 /data/lcc")



    def copy_lcc(self, dev_serial):
        # TODO verify errors
        print "Engineering firmware hase selected."
        print "Copying LCC to /DATA location"
        cmd = 'adb -s {} shell "cp /etc/lcc /data/; chmod 777 /data/lcc"'.format(dev_serial)
        copy_return = self.send_command(cmd)
        if not "errors" in copy_return:
            print "LCC succesfully copied"
        else:
            print "There is problem copying LCC"


    def connect(self):
        print "Trying to connect..."
        """
        1. verify pluged in android devieces
        2. let user  to choose which device will be used

        :return:
        """
        # TODO make sure user input verification works
        try:
            self.dev_list = []
            raw_devs_list = adb_android.devices()[-1].split("\r")
            for items in raw_devs_list:
                if re.search("\n(\S)", items):
                    # print re.search("\n(\S)", items)
                    self.dev = re.search("\n(\S+)\t", items).group(1)
                    self.dev_list.append(self.dev)
            #print "len", len(raw_devs_list)
            if len(self.dev_list) > 1:
                dev_list_index = raw_input("There are more than one units connectes to host. Which one to use?: ")
                while int(dev_list_index)-1 > len(self.dev_list) - 1 or len(dev_list_index) < 1:
                    dev_list_index = raw_input("Please verify your input: ")
                self.adb_device = self.dev_list[int(dev_list_index)-1]
            elif len(self.dev_list) == 1:
                if debug:
                    print "I found only one device connected"
                self.adb_device = self.dev
            if not MP_firmware:
                self.copy_lcc(self.adb_device)
            return self.adb_device
        except:
            raise
            sys.exit("No device connected or unknown error")


    def get_sys_info(self):
        sys_info = {}
        if self.adb_device:
            sys_info["dev_serial"] = self.send_command('adb -s {} shell "getprop ro.serialno"'.format(self.adb_device))
            sys_info["runtime"] = self.send_command('adb -s {} shell "getprop ro.runtime.firstboot"'.format(self.adb_device))
            sys_info["light_serial_no"] = self.send_command('adb -s {} shell "getprop ro.boot.lightserialno"'.format(self.adb_device))
            sys_info["os_build"] = self.send_command('adb -s {} shell "cat /system/build_id"'.format(self.adb_device))
            #print sys_info
            return  sys_info


    def get_local_time(self, date = False):
        if not date:
            curr_time = strftime("%H:%M:%S", localtime())
        else:
            curr_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        return curr_time




    def send_command(self, command, timestamp=False, extra_param = False):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        raw_out = process.communicate()[0]
        if  raw_out is not None:
            ret_value = raw_out.split("\r")[0]
            if timestamp is False:
                return  (ret_value)
            elif timestamp:
                return (self.get_local_time(), ret_value)

    def convert_IEEE_to_float(self,hex_string):
        new_str = ""
        for item in hex_string.split(" ")[::-1]:
            new_str = new_str + item
        float_val = struct.unpack('!f', new_str.decode("hex"))[0]
        return float_val

    def read_voltage(self):
        command_timestamp = False
        cmd = 'adb -s {} shell "cat /sys/class/power_supply/battery/voltage_now"'.format(self.adb_device)
        raw_voltage = self.send_command(cmd, command_timestamp)
        if command_timestamp:
            voltage = "{:.2f}".format(float(raw_voltage[-1])/1000000)
            #print "voltage", voltage
            return (raw_voltage[0], voltage)
        else:

            voltage = "{:.2f}".format(float(raw_voltage)/1000000)
            #print "voltage", voltage
            return float((voltage))

    def read_current(self):
        command_timestamp = False
        cmd = 'adb -s {} shell "cat /sys/class/power_supply/battery/current_now"'.format(self.adb_device)
        raw_current = self.send_command(cmd, command_timestamp)
        if command_timestamp:
            current = "{:.2f}".format(float((raw_current[-1])) / 1000000)
            return raw_current[0], current
        else:
            current = "{:.2f}".format(float(raw_current) / 1000000)
            return float(current)

    def read_SOC_temperature(self):
        command_timestamp = False
        cmd = 'adb -s {} shell "cat /sys/class/thermal/thermal_zone3/temp"'.format(self.adb_device)
        #cmd = 'adb shell "cat /sys/class/thermal/thermal_zone0/temp"'
        try:
            raw_temp = self.send_command(cmd,command_timestamp)
            #print "Raw temperature form L16", raw_temp
            if command_timestamp:
                temperature = float(raw_temp[-1])/10
                return (raw_temp[0], str(temperature))
            else:
                return str(float(raw_temp)/10)
        except:
            print "Unable to read SOC temperature", raw_temp

    def read_asic_temp_kernel(self):
        command_timestamp = False
        cmd = 'adb -s {} shell "logcat -t 100 | grep ThermalEngine"'.format(self.adb_device)
        raw_temp_asic = self.send_command(cmd, command_timestamp)
        #print raw_temp_asic
        if len(raw_temp_asic) > 1:
            temp_temp = str(raw_temp_asic).split(" ")[-1]
            #print "temp _temp", temp_temp
            temperature = re.findall("\d+", temp_temp)
            temperature = str(temperature[-1])[:2]
            if command_timestamp:
                return (raw_temp_asic[0], temperature)
            else:
                return temperature
        else:
            return "N/A"
            print "Cannot find ASIC data from kernel log"

    def read_B4_tepmerature(self):
        if self.isSleeping():
            self.wake_up()
            time.sleep(1)
        cmd = 'adb -s {} shell "./data/lcc -C -m 0 -s 0 -r -p 01 00 1c 02"'.format(self.adb_device)
        read_temp = self.send_command(cmd)
        return self.convert_IEEE_to_float(read_temp)


    def read_asic_log_temp_(self):
        command_timestamp = False
        cmd = 'adb -s {} shell "tail -n 1000 /data/light/asic_1.log | grep -ai --text "temp""'.format(self.adb_device)
        raw_temp_asic = self.send_command(cmd, command_timestamp)
        #print raw_temp_asic
        if len(raw_temp_asic) > 1:
             temp_temp = raw_temp_asic.split(" ")[-1]

             temperature = temp_temp.split(".")[0]
             return temperature
        else:
            return "N/A"
            print "Cannot find ASIC temp data from ASIC1 log"



    def capture_LCC(self, mode):
        if mode == 1: # TORCH
            self.send_command('""')
        elif mode == 2 : # flashligt
            self.send_command('""')
        elif mode ==3: #  burst capture_LCC
            self.send_command('""')
        elif mode == 4: # all modules
            self.send_command('adb -s {} shell "cd data; ./lcc -m 0 -s 0 -f 1 01 00 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000"'.format(self.adb_device))
        elif mode == 5:# single asic capture_LCC which one?
            self.send_command('adb -s {} shell "cd data; ./lcc -m 0 -s 0 -f 1 A2 86 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000"'.format(self.adb_device))
        elif mode == 6: # preview
            self.send_command('""')

    def find_file_count(self):
        """
        to control storage use
        :return: how many files in camera directory
        """
        command_timestamp = False
        cmd = 'adb -s {} shell "ls /sdcard/DCIM/Camera/ | wc -l"'.format(self.adb_device)
        files_count = self.send_command(cmd, command_timestamp)
        return files_count

    def remove_files(self):
        command_timestamp =False
        cmd = 'adb -s {} shell "rm -r /sdcard/DCIM/Camera/*"'.format(self.adb_device)
        rem_file_out = self.send_command(cmd, command_timestamp)
        return "Done"

    def parse_ASIC_fatal_errors(self):
        #keyword = "debug"
        #keyword = "temp\|info"
        keyword = "fatal"
        self.ASIC_error_list = []
        #cmd = 'adb shell "logcat -d | grep -E %s"'%keyword #kernel logs
        for i in range(1,4):
            cmd = 'adb -s {} shell "tail -n 1000 /data/light/asic_{}.log | grep -Ei {}'.format(self.adb_device,i,keyword)
            #print cmd
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out = process.communicate()[0]
            errors = out
            #print SOC_errors
            for lines in errors.split("\n"):
                if len(lines) > 1:
                    #print "lines", lines
                    self.ASIC_error_list.append(self.get_local_time(True) + ":--" + lines.strip() + "\n")
        return self.ASIC_error_list

    def parse_SOC_fatal_errors(self):
        #keyword = "debug"
        #keyword = "temp\|info"
        keyword = "fatal\|error"
        self.SOC_error_list = []
        cmd = 'adb -s {} shell "logcat -d | grep -E {}"'.format(self.adb_device, keyword) #kernel logs
        for i in range(1,4):
            #cmd = 'adb shell "tail -n 1000 /data/light/asic_{}.log | grep -Ei {}'.format(i,keyword)
            #print cmd
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out = process.communicate()[0]
            errors = out
            #print SOC_errors
            for lines in errors.split("\n"):
                if len(lines) > 1:
                    #print "lines", lines
                    self.SOC_error_list.append(self.get_local_time(True) + ":--" + lines.strip()+"\n")
        return self.SOC_error_list

    def charge_enabled(self,need_charge):
        if need_charge:
            #enable charging
            cmd = 'adb -s {} shell "echo 1 > /sys/class/power_supply/battery/charging_enabled"'.format(self.adb_device)
        else:
            # disable charging
            cmd = 'adb -s {} shell "echo 0 > /sys/class/power_supply/battery/charging_enabled"'.format(self.adb_device)
        charge_status = self.send_command(cmd)
        return charge_status




    def adbCapture(self):

        #self.wakeup_or_run()
        #print "capturing "
        if int(self.find_file_count()) > 1500:
            self.remove_files()
        # TODO add method to sefl delete pics if it more than 800
        self.checkifCrash()
        global DEBUG
        DEBUG = False
        if DEBUG:
            print 'DEBUG Capture'
            return
        if self.isSleeping():
            print "Screen is off, trying to wakeup"
            self.wakeup_or_run(0)
        cmd = 'adb -s {} shell input keyevent 27'.format(self.adb_device)  # 27
        self.send_command(cmd)
        #print ' Capturing Image'
        return "Done"

    def isSleeping(self):
        state = self.send_command('adb -s {} shell dumpsys display | findstr \"mScreenState\"'.format(self.adb_device))
        if 'ON' in state:
            #print 'Screen On'
            return False
        else:
            if debug:
                print 'Screen Off'
            return True

    def force_sleep(self, cycle_pause=0):
        #print "cycle_pause",cycle_pause
        """
        let say main function will call this every 60 minutes
        based on that interval every 5 sec run command
        :param loop_cycle:
        :return:
        """
        if cycle_pause ==0:
            print "Forcing to sleep"
            if not self.isSleeping():
                ut_sleep = self.send_command('adb -s {} shell input keyevent 26'.format(self.adb_device))
        elif cycle_pause > 0:
            print "Forcing to sleep entire timeout"
            self.send_command('adb -s {} shell input keyevent 26'.format(self.adb_device))
            time.sleep(cycle_pause)

    def wakeup_or_run(self, cycle_pause, use_capture = 0, ASICs_gr=0):
        avg_curr_list = []
        avg_volt_list = []
        wake_up = None # to return status
        #print "cycle pause", cycle_pause
        """
        :param cycle_pause:seconds
        :return:
        minimum screen timneout is 15 sec in settings
        """
        sleep_seconds1 = 10  # Adjusting timing because if rutine time variation
        sleep_seconds2 = 1
        if ASICs_gr <= 1:
            self.adbZoom28()
        elif ASICs_gr == 2:
            self.adbZoom150()
        while cycle_pause >= 0: # "=" included to run without pause as well
            if use_capture == 0:  # No capture
                wake_up = self.send_command('adb -s {} shell input keyevent 82'.format(self.adb_device))
                time.sleep(sleep_seconds1)
                cycle_pause = cycle_pause - sleep_seconds1

            elif use_capture == 1:
                #print "capturing"
                time.sleep(sleep_seconds2)
                wake_up = self.adbCapture()
                voltage = self.read_voltage()
                current = self.read_current()
                cycle_pause = cycle_pause - sleep_seconds2 - 3  # 15 is overhead while running zoom, etc.
                avg_curr_list.append(current)
                avg_volt_list.append(voltage)

            elif use_capture == 2:  # Preview only
                wake_up = self.send_command('adb -s {} shell input keyevent 82'.format(self.adb_device))
                voltage = self.read_voltage()
                current = self.read_current()
                avg_curr_list.append(current)
                avg_volt_list.append(voltage)
                time.sleep(sleep_seconds1)
                cycle_pause = cycle_pause - sleep_seconds1

        if len(avg_curr_list) == len(avg_curr_list) > 0 and len(avg_curr_list) > 0:
            #self.resetUI()
            return (avg_curr_list, avg_volt_list)
        else:
            #self.resetUI()
            return False
        return wake_up

    def wake_up(self,cycle_pause=0):
        if cycle_pause ==0:
            wake_up_st = self.send_command('adb -s {} shell input keyevent 82'.format(self.adb_device))
        else:
            while cycle_pause >= 10:
                start_wake_time = time.time()
                wake_up_st = self.send_command('adb -s {} shell input keyevent 82'.format(self.adb_device))
                stop_wake_time = time.time()
                wake_sleep_dur = stop_wake_time-start_wake_time
                #print "will slleep, duration",wake_sleep_dur
                time.sleep(10-wake_sleep_dur)
                cycle_pause -= 10
                #print "waking up, remainig time %d"%cycle_pause
                if debug:
                    print "time takes for wake",time.time()-start_wake_time

    def startLightapp(self):
        self.send_command('adb -s {} shell am start -n light.co.lightcamera/light.co.camera.CameraActivity '.format(self.adb_device))
        time.sleep(5)

    def checkifCrash(self):
        while True:
            activity = self.send_command('adb -s {} shell dumpsys activity activities | findstr \"mFocusedActivity\"'.format(self.adb_device))
            time.sleep(1)
            if 'light.co.camera.CameraActivity' in activity:
                return False
            else:
                print "Light APP has crashed, restarting the app"
                self.startLightapp()
                time.sleep(8)
        #return (activity)

    def enableLogs(self):
        self.send_command('adb -s {} shell setprop persist.light.asic.debug disabled'.format(self.adb_device))
        time.sleep(1)

    def lockScreen(self):
        self.send_command('adb -s {} shell input keyevent 26'.format(self.adb_device))

    def batteryCharged(self):
        #TODO correct
        query_str = "adb -s {} shell dumpsys battery | findstr \"level\"".format(self.adb_device)
        level = self.send_command(query_str)
        level = level[9:12]
        try:
            if 10         < int(level):
                #print "Battery has {}% charge".format(level.rstrip())
                return int(level)
            else:
                print "Battery charge level is critical:  " + level.rstrip() + "%"
                return False
        except:

            print "Needs charged " + level + '%'
            return False


    # Autofocus center of preview
    def adbCenterAF(self, X, Y): # TODO double check
        self.checkifCrash()
        cmd = 'adb -s {} shell input tap '.format(self.adb_device) + str(L16.X) + ' ' + str(L16.Y)
        self.send_command(cmd)
        print '\nAutofocus Center'
        time.sleep(1.5)

    # Zooms in 1 step (narrower fov increase focal length)
    def adbZoomIn(self):
        self.checkifCrash()
        dist = 40
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(L16.Y) + ' ' + str(L16.X) + ' ' + str(L16.Y - dist) + ' 500'
        self.send_command(cmd)
        time.sleep(0.5)

    # Zooms in 10mm more
    def adbZoomIn10(self):
        self.checkifCrash()
        # steps = 5.7  # 10mm more is this many zoom increments for 215
        steps = 1.6  # User build 200 and later
        startY = 1079
        endY = startY - steps * L16.D
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1000'
        self.send_command(cmd)
        time.sleep(1)

    def adbZoomOut10(self):
        self.checkifCrash()
        # steps = 5.7  # 10mm more is this many zoom increments
        steps = 1.6
        startY = 1079
        endY = startY + steps * L16.D
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1000'
        self.send_command(cmd)
        time.sleep(1)

    # Zooms out 1 step (wider fov decrease focal length)
    def adbZoomOut(self):
        self.checkifCrash()
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(L16.Y) + ' ' + str(L16.X) + ' ' + str(L16.Y + L16.D) + ' 500'
        self.send_command(cmd)
        time.sleep(0.5)

    #Go to 28mm
    def adbZoom28(self):
        self.checkifCrash()
        # startY = 100  # for 215
        startY = 500
        endY = startY + 10 * L16.D
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1500'
        self.send_command(cmd)
        #print '\nZoom set to 28mm'
        time.sleep(1)
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1500'
        self.send_command(cmd)
        time.sleep(0)

    # Go to 70mm
    def adbZoom70(self):
        self.checkifCrash()
        steps = 5.8  # 70mm is this many zoom increments from 28mm
        # steps = 22  # 70mm is this many zoom increments from 28mm for 215
        startY = 1079
        endY = startY - steps * L16.D
        self.adbZoom28()  # Reset to widest...
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 4000'
        self.send_command(cmd)
        print '    Zoom set to 70mm'
        time.sleep(4)


    # Go to 150mm
    def adbZoom150(self):
        self.checkifCrash()
        cmd = 'adb -s {} shell input swipe '.format(self.adb_device) + str(L16.X) + ' ' + str(1079) + ' ' + str(L16.X) + ' ' + str(-100 * L16.D) + ' 2000'
        self.send_command(cmd)
        #print '\nZoom set to 150mm'
        time.sleep(1)

    def resetUI(self):
        self.checkifCrash()
        time.sleep(2)
        self.adbZoom28()
        time.sleep(2)
        self.adbZoom28()
        time.sleep(2)

        self.send_command('adb -s {} shell input swipe '.format(self.adb_device) + L16.SS_button_x + ' ' + L16.SS_button_y + ' ' + L16.SS_button_x +
                L16.reset + ' ' + '200')

        time.sleep(1.5)

        self.send_command('adb -s {} shell input swipe '.format(self.adb_device) + L16.SS_button_x + ' ' + L16.SS_button_y + ' ' + L16.SS_button_x +
                L16.reset + ' ' + '200')
        time.sleep(1.5)

        self.send_command('adb -s {} shell input swipe '.format(self.adb_device) + L16.ISO_button_x + ' ' + L16.ISO_button_y + ' ' + L16.ISO_button_x +
                L16.reset + ' ' + '500')

        time.sleep(1.5)

        self.send_command('adb -s {} shell input swipe '.format(self.adb_device) + L16.ISO_button_x + ' ' + L16.ISO_button_y + ' ' + L16.ISO_button_x +
                L16.reset + ' ' + '500')

        time.sleep(1.5)

        self.checkifCrash()

     ###################################################


if debug:
    camera = L16()
    print camera.get_sys_info()["dev_serial"]
    camera.read_B4_tepmerature()
    #print camera.convert_IEEE_to_float("00 00 DB 41")
    """
    #print (camera.send_command(cmd))
    print  camera.read_voltage()
    time.sleep(1)
    print camera.read_current()
    time.sleep(1)
    print camera.read_SOC_temperature()
    time.sleep(1)
    print "asic temp", camera.read_asic_temp_kernel()
    time.sleep(1)
    print camera.get_sys_info()
    time.sleep(1)
    print camera.get_local_time()
    time.sleep(1)
    print camera.read_voltage()
    time.sleep(1)
    print camera.read_current()
    time.sleep(1)
    print camera.read_SOC_temperature()
    time.sleep(1)
    print camera.batteryCharged()
    time.sleep(1)
    print camera.isSleeping()
    time.sleep(1)
    #print camera.wakeup_or_run()
    time.sleep(1)
    print "ret", camera.parse_ASIC_fatal_errors()
    """
    #print camera.read_asic_temp_kernel()
    #print camera.read_asic_log_temp_()
    #print camera.parse_SOC_fatal_errors()
    #print camera.resetUI()
    #print camera.checkifCrash()
    #print camera.connect(), "sn"
