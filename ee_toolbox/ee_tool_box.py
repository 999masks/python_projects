import re

import time
import sys

from os import system
import subprocess
import shlex
import tempfile
import commands
import cmd



from adbandroid import adb_android

from Tkinter import *
from Tkinter import  Tk, Label, Button, W, StringVar


import os
from win32com.client import GetObject

#####plan####
# 1. init conn
# chck root
# enabli asig log - done
# dump sys logs
# parse logs
# asic reset - done
# run custom command
# save logs
# parese set_prob
# open teraterm terminal - done
#  Asic flash
# close all terminals - done




class Toolbox:
    def __init__(self):
        self.dev_list = []
        self.adb_obj = adb_android

        self.adb_obj.start_server()
        self.connect()
        print "Server connected"

    def check_pluged_devs(self):
        #TODO this function will return list of serial numbers of conected devices
        pass

    def connect(self):
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
        #can we have one return?




    def adb_comm_send(self, command):
        # TODO reformat command if it is multiple
        return self.adb_obj.shell(command)



    """
    def shell_execute(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        print "debug", process.communicate()[0]
        return process
    """

    def shell_execute(self, command):
        with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(["tasklist"], stdout=tempf)
            proc.wait()
            tempf.seek(0)
            print tempf.read()


    def run_command(self, command):
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, shell=True)
        while True:
            output = process.stdout.readline()

        rc = output
        return rc


    def asic_reset(self):
        self.adb_comm_send("cp /system/etc/prog_app_p2 /data; chmod 777 /data/prog_app_p2")
        self.adb_comm_send("/data/prog_app_p2 -q")

    def asic_debug_term(self):
        pass

    def asic_flash(self, file_loc):
        # TODO browse file with specific name and extension

        self.adb_comm_send("cp /system/etc/prog_app_p2 /data; chmod 777 /data/prog_app_p2")

        curr_version = subprocess.Popen(shlex.split("adb shell './data/prog_app_p2 -v'"), stdout=subprocess.PIPE,
                                        shell=True)
        api_version= curr_version.stdout.read()
        print "API verison is : ", api_version.split("\r")[2][13:23]

        asic1_fw = file_loc[0].split("/")[-1]
        asic2_fw = file_loc[1].split("/")[-1]
        asic3_fw = file_loc[2].split("/")[-1]
        print "asics name", asic1_fw, asic2_fw, asic3_fw

        for item in file_loc[:1]: #just for asic 1 test
            adb_android.push(item, "/data/")
            process = subprocess.Popen(shlex.split("adb shell 'ls /data/'"), stdout=subprocess.PIPE, shell=True)
            print "pushing files are done ", process.stdout.readline()
            #renaming the files
            curr_file_name = item.split("/")[-1]
            asic_number = file_loc.index(item)+1
            #adb_android.shell(("mv /data/%s"%(curr_file_name), "/data/ASIC%s.bin"%asic_number))
            adb_android.shell(("'rm /data/ASIC1_2017-08-03-12-53-08.bin', 'ASIC1.bin"))
            flashing_out = "./data/prog_app_p2 -i spi -m program -f %s"%(item.split("/")[-1])
            #flash_comm = subprocess.Popen(shlex.split(), stdout=subprocess.PIPE, shell=True)
            adb_android.shell(flashing_out)
            time.sleep(1)



    def log_parse(self):
        #cmd = "adb shell miniterm -s 460800 /dev/ttyHSL1"
        cmd = "ls"
        print commands.getoutput(('echo "test" | wc'))
        # with tempfile.TemporaryFile() as tempf:
        #     proc = subprocess.Popen(cmd, stdout=tempf)
        #     proc.wait()
        #     tempf.seek()
        #     #print tempf.read()


    def realitime_log(self, command):
        pass
        #proc = subprocess.check_output(command)
        #subprocess.call([command])
        #proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        #proc = system("start powershell -NoExit adb shell dir")


        log_file = open("debug.log", "w")
        # print proc
        # line = proc.communicate()[0]
        # print "log _line ", line
        # while line:
        #     log_file.write(line)
        log_file.close()

    def save_result(self):
        pass

    def enable_asic_logging(self):
        system("adb root")
        system("adb remount")
        self.adb_comm_send("setprop persist.light.asic.debug disabled; sync")
        system("adb reboot")
        adb_android.wait_for_device()


    def asic_logging(self):
        #self.enable_asic_logging()
        time.sleep(1)
        system("adb wait-for-devices")
        system("$host.ui.RawUI.WindowTitle = 'ASIC 1'") # to enable custom title
        system("start powershell -NoExit adb shell miniterm -s 460800 /dev/ttyHSL1")
        system("start powershell -NoExit adb shell miniterm -s 460800 /dev/ttyHSL2")
        system("start powershell -NoExit adb shell miniterm -s 460800 /dev/ttyHSL3")


    # def asic_logging(self):
    #     self.enable_asic_logging()
    #     time.sleep(1)
    #     system("adb wait-for-devices")
    #     log_file = open("log.log", "w")
    #     log_lines = self.run_command("start powershell -NoExit adb shell miniterm -s 460800 /dev/ttyHSL1")
    #     #print log_lines
    #     while log_lines:
    #         log_file.write(log_lines)
    #     log_file.close()

        #system("$host.ui.RawUI.WindowTitle = 'ASIC 1'") # to enable custom title
        #self.shell_execute("start powershell -NoExit adb shell miniterm -s 460800 /dev/ttyHSL2")
        #self.shell_execute("start powershell -NoExit adb shell miniterm -s 460800 /dev/ttyHSL3")


    def dump_hardware_info(self):
        pass



    def capture(self):
        pass







class toolbox_gui:

    def __init__(self, master):
        self.master = master
        master.title = "EE toolbox"

        self.label = Label(master, text=" Control buttons")
        self.label.grid(columnspan =2, sticky=W)

        self.enable_asic_logs_but = Button(master, text="Enable Asic logging",
                                           command=l16.enable_asic_logging)
        # TODO add text please wait while system reboots, when this button got pressed
        self.enable_asic_logs_but.grid(row=1, padx=10, pady=10, sticky=W)

        self.run_asic_debug_log = Button(master, text="Run terminals for Asic loging",
                                          command=Toolbox().asic_logging)
        self.run_asic_debug_log.grid(row=1, padx=10, pady=10, sticky=W)

        self.run_asic_reset = Button(master, text="Asic reset",
                                         command=Toolbox().asic_reset)
        self.run_asic_reset.grid(row=3, padx=10, pady=10, sticky=W)

        self.close_all_consoles = Button(master, text="Close consoles",
                                         command=self.close_consoles)
        self.close_all_consoles.grid(row=5,padx=10, pady=10, sticky=W)

        self.asic_flash = Button(master, text="Flash firmware, please select the files",
                                         command=self.browse_for_files)
        self.asic_flash.grid(row=6, padx=10, pady=10, sticky=W)

        self.title_keyword = Label(master, text = "Filter logs by keyword")
        self.title_keyword.grid(row=1, column = 2, padx=10)

        self.keyword_filter = Entry(master, width = 10)
        self.keyword_filter.grid(row=2, column=2)


        self.export_log = Button(master, text = "Export log files", command = lambda: None)
        self.export_log.grid(row =3, column = 2, padx = 10, pady=10)

        self.current_value = StringVar(master, "No files")
        self.file_selected = Label(master, textvariable = self.current_value)

        self.file_selected.grid(row=6, column = 2)
        # TODO crate function to genrate separate button to each connected device
        # TODO keep main window always on top

        self.keyword= StringVar(master, "Nothing is filtering")
        self.keyword_label = Label(master, textvariable = self.keyword)
        self.keyword_label.grid(row = 2, column = 6 )

        master.bind("<Return>", lambda x: self.filter_by_keyword())


    def close_consoles(self):
        WMI = GetObject("winmgmts:")
        process = WMI.InstancesOf("Win32_Process")

        for windows in WMI.ExecQuery('select * from Win32_Process where Name="powershell.exe"'):
            #print "Killing PID:", windows.Properties_('ProcessId').Value
            os.system("taskkill /pid "+str(windows.Properties_('ProcessId').Value))

    asic_fw_files = []

    def browse_for_files(self):
        FW_1 = "ASIC 1: "
        FW_2 = "ASIC 2: "
        FW_3 = "ASIC 3: "

        while len(self.asic_fw_files) <3:
            print "asic fw", len(self.asic_fw_files)
            from tkFileDialog import askopenfile
            Tk().withdraw()
            filename = askopenfile()
            self.asic_fw_files.append(str(filename.name))


            if len(self.asic_fw_files)== 1:
                FW_1 = FW_1 + ((str(self.asic_fw_files[-1])).split("/"))[-1]

            elif len(self.asic_fw_files)== 2:
                FW_2 = FW_2 + ((str(self.asic_fw_files[-1])).split("/"))[-1]

            elif len(self.asic_fw_files)== 3:
                FW_3 = FW_3 + ((str(self.asic_fw_files[-1])).split("/"))[-1]

            self.current_value.set(FW_1 + "\r" + FW_2 + "\r" + FW_3)

            #print self.keyword_filter.get()

        print "All 3 asics files have benn selected", self.asic_fw_files
        Toolbox().asic_flash(self.asic_fw_files)

    def filter_by_keyword(self):
        self.keyword.set("Filtering logs by: " + self.keyword_filter.get())

        print "keyword", self.keyword


l16 = Toolbox()

command = 'adb shell'
l16.realitime_log(command)

root = Tk()
l17 = toolbox_gui(root)
root.mainloop()

#print l17.adb_device
#l16.adb_comm_send("pwd; ls")
#l16.asic_reset()
#l16.enable_asic_logging()
#l16.asic_logging()
#l16.log_parse()

#l16.enable_asic_logging()

