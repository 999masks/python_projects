from adbandroid import adb_android
import re
import sys
import subprocess

import time
from time import strftime, localtime





#TODO read temp sensors
# LCC captures
class L16:
    D = 60  # for User Build 200 and later
    T = 400  # Choose time in ms to swipe D pixels (affects consistency of zoom amount)
    X = 1920 / 2  # Center horizontal touchscreen pixel location
    Y = 1080 / 2  # Center vertical touchscreen pixel location

    def __init__(self):
        self.dev_list = []
        self.adb_obj = adb_android
        self.adb_obj.start_server()
        self.connect()
        print "Server connected"
        #uncomment if you need to use LCC for capture_LCC
        # print "Trying to copy LCC binary to /data/ dir\r "
        # adb_android.shell("cp /etc/lcc /data/; chmod 777 /data/lcc")
        # print "LCC succesfully copied"

    def connect(self):
        self.dev_list = []
        raw_devs_list = adb_android.devices()[-1].split("\r")
        for items in raw_devs_list:
            if re.search("\n(\S)", items):
                # print re.search("\n(\S)", items)
                self.dev = re.search("\n(\S+)\t", items).group(1)
                self.dev_list.append(self.dev)
        # print "len", len(dev_list)
        if len(self.dev_list) > 1:
            dev_list_index = raw_input("There are more than one item connectes to host. Which one to use?: ")
            while int(dev_list_index) > len(self.dev_list) - 1 or len(dev_list_index) < 1:
                dev_list_index = raw_input("Please verify your input: ")
            self.adb_device = self.dev_list[int(dev_list_index)]
            return self.adb_device
        elif len(self.dev_list) == 1:
            print "Only one device"
            self.adb_device = self.dev
            return self.adb_device
        else:
            sys.exit("No device connected or unknown error")

    #TODO ask rick to prevent charging
    def get_sys_info(self):
        sys_info = {}
        sys_info["dev_serial"] = self.send_command('adb shell "getprop ro.serialno"')
        #sys_info["runtime"] = adb_android.shell("getprop ro.serialno") #works need extra formatting
        sys_info["runtime"] = self.send_command('adb shell "getprop ro.runtime.firstboot"')
        sys_info["light_serial_no"] = self.send_command('adb shell "getprop ro.boot.lightserialno"')
        sys_info["os_build"] = self.send_command('adb shell "cat /system/build_id"')
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

    def read_voltage(self):
        command_timestamp = False
        cmd = 'adb shell "cat /sys/class/power_supply/battery/voltage_now"'
        raw_voltage = self.send_command(cmd, command_timestamp)
        if command_timestamp:
            voltage = "{:.2f}".format(float(raw_voltage[-1])/1000000)
            print "voltage", voltage
            return (raw_voltage[0], voltage)
        else:

            voltage = "{:.2f}".format(float(raw_voltage)/1000000)
            print "voltage", voltage
            return (voltage)

    def read_current(self):
        command_timestamp = False
        cmd = 'adb shell "cat /sys/class/power_supply/battery/current_now"'
        raw_current = self.send_command(cmd, command_timestamp)
        if command_timestamp:
            current = "{:.2f}".format(float((raw_current[-1])) / 1000000)
            return raw_current[0], current
        else:
            current = "{:.2f}".format(float(raw_current) / 1000000)
            return current

    def read_SOC_temperature(self):
        command_timestamp = False
        cmd = 'adb shell "cat /sys/class/thermal/thermal_zone3/temp"'
        #cmd = 'adb shell "cat /sys/class/thermal/thermal_zone0/temp"'
        raw_temp = self.send_command(cmd,command_timestamp)
        if command_timestamp:
            temperature = float(raw_temp[-1])/10
            return (raw_temp[0], str(temperature))
        else:
            return str(float(raw_temp)/10)

    def read_asic_temp(self):
        command_timestamp = False
        cmd = 'adb shell "logcat -t 1 | grep ThermalEngine"'
        raw_temp_asic = self.send_command(cmd, command_timestamp)
        if len(raw_temp_asic) > 1:
            temperature = re.findall("\d+", raw_temp_asic[-1])
            temperature = str(temperature[-1].split(" ")[-1])
            if command_timestamp:
                return (raw_temp_asic[0], temperature)
            else:
                return temperature
        else:
            print "No temp data availabe"

    def capture_LCC(self, mode):
        if mode == 1: # TORCH
            adb_android.shell("cp /etc/lcc /data/; chmod 777 /data/lcc")
            print "LCC succesfully copied"
            self.send_command('""')
        elif mode == 2 : # flashligt
            self.send_command('""')
        elif mode ==3: #  burst capture_LCC
            self.send_command('""')
        elif mode == 4: # all modules
            self.send_command('adb shell "cd data; ./lcc -m 0 -s 0 -f 1 01 00 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000"')
        elif mode == 5:# single asic capture_LCC which one?
            self.send_command('adb shell "cd data; ./lcc -m 0 -s 0 -f 1 A2 86 00 11 21 00 -R 4160,3120 -g 7.75 -e 40000000"')
        elif mode == 6: # preview
            self.send_command('""')

    #####################################
    # JACE code
    def adbCapture(self):
        self.checkifCrash()
        global DEBUG
        if DEBUG:
            print 'DEBUG Capture'
            return
        cmd = 'adb shell input keyevent KEYCODE_CAMERA'  # 27
        self.send_command(cmd)
        print '    Capturing Image'
        time.sleep(.5)

    def isSleeping(self):
        state = self.send_command('adb shell dumpsys display | findstr \"mScreenState\"')
        if 'ON' in state:
            #print 'Screen On'
            return False
        else:
            print 'Screen Off'
            return True

    def force_sleep(self):
        if not self.isSleeping():
            put_sleep = self.send_command('adb shell input keyevent 26')

    def wakeupScreen(self,continous=False):
        # duration in minutes
        # TODO add option to keep display on until program finishes
        keep_going = True
        if continous:
             while continous and keep_going:
                if self.isSleeping():
                    print "Waking up Screen"
                    self.send_command('adb shell input keyevent 82')
                else:
                    print "Display is on"
                print "iteration is happening, remainin time: %d minutes"
                time.sleep(10)
        else:
            if self.isSleeping():
                self.send_command('adb shell input keyevent 82')
            #time.sleep(1)
        return True

    def startLightapp(self):
        self.send_command('adb shell am start -n light.co.lightcamera/light.co.camera.CameraActivity ')
        time.sleep(5)

    def checkifCrash(self):
        while True:
            activity = self.send_command('adb shell dumpsys activity activities | findstr \"mFocusedActivity\"')
            time.sleep(1)
            if 'light.co.camera.CameraActivity' in activity:
                return False
            else:
                print "APP CRASH, RESTARTING APP"
                self.startLightapp()
                time.sleep(10)

    def enableLogs(self):
        self.send_command('adb shell setprop persist.light.asic.debug disabled')
        time.sleep(1)

    def lockScreen(self):
        self.send_command('adb shell input keyevent 26')

    def batteryCharged(self):
        query_str = "adb shell dumpsys battery | findstr \"level\""
        level = self.send_command(query_str)
        level = level[9:12]
        try:
            if 30 < int(level):
                print "CHARGED UP TO: " + level.rstrip() + "%"
                return True
            else:
                print "Needs charged, Battery at " + level.rstrip() + "%"
                return False
        except:
            print "Needs charged" + level + '%'
            return False

    # Autofocus center of preview
    def adbCenterAF(self, X, Y): # TODO double check
        self.checkifCrash()
        cmd = 'adb shell input tap ' + str(L16.X) + ' ' + str(L16.Y)
        self.send_command(cmd)
        print '\nAutofocus Center'
        time.sleep(1.5)

    # Zooms in 1 step (narrower fov increase focal length)
    def adbZoomIn(self):
        self.checkifCrash()
        dist = 40
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(L16.Y) + ' ' + str(L16.X) + ' ' + str(L16.Y - dist) + ' 500'
        self.send_command(cmd)
        time.sleep(0.5)

    # Zooms in 10mm more
    def adbZoomIn10(self):
        self.checkifCrash()
        # steps = 5.7  # 10mm more is this many zoom increments for 215
        steps = 1.6  # User build 200 and later
        startY = 1079
        endY = startY - steps * L16.D
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1000'
        self.send_command(cmd)
        time.sleep(1)

    def adbZoomOut10(self):
        self.checkifCrash()
        # steps = 5.7  # 10mm more is this many zoom increments
        steps = 1.6
        startY = 1079
        endY = startY + steps * D
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1000'
        self.send_command(cmd)
        time.sleep(1)

    # Zooms out 1 step (wider fov decrease focal length)
    def adbZoomOut(self):
        self.checkifCrash()
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(L16.Y) + ' ' + str(L16.X) + ' ' + str(L16.Y + L16.D) + ' 500'
        self.send_command(cmd)
        time.sleep(0.5)

    #Go to 28mm
    def adbZoom28(self):
        self.checkifCrash()
        # startY = 100  # for 215
        startY = 500
        endY = startY + 10 * L16.D
        cmd = 'adb shell input swipe ' + str(X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1500'
        self.send_command(cmd)
        print '\nZoom set to 28mm'
        time.sleep(4)
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 1500'
        self.send_command(cmd)
        time.sleep(4)

    # Go to 70mm
    def adbZoom70(self):
        self.checkifCrash()
        steps = 5.8  # 70mm is this many zoom increments from 28mm
        # steps = 22  # 70mm is this many zoom increments from 28mm for 215
        startY = 1079
        endY = startY - steps * L16.D
        self.adbZoom28()  # Reset to widest...
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(startY) + ' ' + str(L16.X) + ' ' + str(endY) + ' 4000'
        self.send_command(cmd)
        print '    Zoom set to 70mm'
        time.sleep(4)


    # Go to 150mm
    def adbZoom150(self):
        self.checkifCrash()
        cmd = 'adb shell input swipe ' + str(L16.X) + ' ' + str(1079) + ' ' + str(L16.X) + ' ' + str(-100 * L16.D) + ' 2000'
        self.send_command(cmd)
        print '\nZoom set to 150mm'
        time.sleep(1)

    ###################################################
"""

#camera = L16()
#print (camera.send_command(cmd))
#print  camera.read_voltage()
#print camera.read_current()
#print camera.read_SOC_temperature()
#print "asic temp", camera.read_asic_temp()
#print camera.get_sys_info()
#print camera.get_local_time()
#print camera.read_voltage()
#print camera.read_current()
#print camera.read_SOC_temperature()
#print camera.batteryCharged()
#print camera.isSleeping()
#print camera.wakeupScreen()
#main_func(2)
"""
