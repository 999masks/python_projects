from L16 import *
#import run_character
from Tkinter import Tk, Label, Button, Entry, IntVar, END, W,E,S,N,NW, StringVar, Radiobutton, Checkbutton
import sys

from matplotlib import pyplot as plt
from matplotlib.artist import setp

from time import strftime, localtime
import os
import time
import sys

class Execute():
    def __init__(self):
        self.DUT = L16()

    def export_data(self):

        file_path = os.path.join(os.environ["HOMEPATH"], os.path.join("Desktop", "L16_temp_characterization_%s.csv" % (
            strftime("%Y_%m_%d", localtime()))))
        # print file_path
        rep_file_obj = open(file_path, "w")
        top_row = (
            "Time,SOC temperature, CCB temperature, Battery current, Battery voltage, Battery Capacity, Is charging\r")
        rep_file_obj.write(top_row)

        for rows in self.data_set.items():
            print "current row", rows
            # temp_row = ""
            temp_row = str(rows[0])
            # print temp_row
            for data in rows[1]:
                print "str values", str(data)
                temp_row = str(temp_row) + "," + str(data)
                # new = "".join(temp_row + "data")
                print "temp_row mod", temp_row
            rep_file_obj.write((temp_row + "\r"))
        rep_file_obj.close()
        print "file closed"

    def run_it(self):
        self.iterations = None
        self.duration = None
        self.read_all_fields()
        #read inputs from gui and sent to main func
        self.run_by_time = L16_GUI.var.get()
        self.entry_data = (L16_GUI.iteration_or_time.get()) #how long or how many iterations?
        self.zoom_level = L16_GUI.ASICs_gr.get() # will determine which ASIC group will be used
        self.power_mode = L16_GUI.standby_wake.get()
        self.cont_cap = L16_GUI.cont_cap_val.get()
        if not len(self.entry_data) <1 or self.run_by_time < 1: # or \
                #self.zoom_level < 1 or self.power_mode < 1 or self.cont_cap < 1:
            print "data", self.entry_data, self.run_by_time
            if self.run_by_time == 2: # time_iteration radiobuttom value
                self.iterations = int(self.entry_data)
            elif self.run_by_time == 1:
                duration = int(self.entry_data)
            else:
                print ("Please check that all field is marked")

            self.main_func(self.run_by_time, self.iterations, self.zoom_level, self.power_mode, self.cont_cap)
            L16_GUI.curent_status_var.set("Current status: RUNNING")
        else:
            sys.exit("wrong data is entered")
            #camera = L16()

    def read_all_fields(self):# can be deleted

        print "By time", L16_GUI.var.get()  # good 0 - unchecked,1,2
        # print "By iteration",
        print "entry field", L16_GUI.iteration_or_time.get()  # good
        print "Asic 1,2", L16_GUI.ASICs_gr.get()  # good
        # print "Asic 23",
        print "Force stanby", L16_GUI.standby_wake.get()  # good 0 - unchecked,1,2
        # print "keep awake",
        print "continious capture", L16_GUI.cont_cap_val.get()  # good 0,1




    def plotting(self, data_set, serial):
        x_1 = range(1, (data_set.__len__() + 1))
        y_core_temp = []
        y_voltage = []
        y_asic_temp = []
        y_current = []
        x_labels = sorted(data_set.keys())  # timestamp as a label

        for item in x_labels:
            y_core_temp.append(data_set[item][0])
            y_asic_temp.append(data_set[item][1])
            y_current.append(data_set[item][2])
            y_voltage.append(data_set[item][3])

        fig = plt.figure()
        host = fig.add_subplot(111)

        par1 = host.twinx()
        par2 = host.twinx()
        par3 = host.twinx()

        host.set_xlabel("Time")
        host.set_ylabel("Temperature")
        par1.set_ylabel("Voltage")
        par2.set_ylabel("Current")

        host.set_ylim(-10, 75)
        par1.set_ylim(0, 5)
        par2.set_ylim(-2, 3)

        color1 = plt.cm.viridis(0)
        color2 = plt.cm.viridis(0.5)
        color3 = plt.cm.plasma(.9)
        color4 = plt.cm.inferno(.7)

        plt.xticks(x_1, x_labels)
        setp(host.get_xticklabels(), rotation=90)  # rotate time label

        p1, = host.plot(x_1, y_core_temp, color=color1, label="SOC Temp")
        p2, = par1.plot(x_1, y_asic_temp, color=color2, label="CCB Temp")
        p3, = par2.plot(x_1, y_current, color=color3, label="B. Current")
        p4, = par3.plot(x_1, y_voltage, color=color4, label="B. Voltage")

        # legend in chart
        lns = [p1, p2, p3, p4]
        host.legend(handles=lns, loc='best')

        # right, left, top, bottom
        par2.spines['right'].set_position(('outward', 25))

        # TODO colors are mismatched
        host.yaxis.label.set_color(p1.get_color())
        par1.yaxis.label.set_color(p2.get_color())
        par2.yaxis.label.set_color(p3.get_color())
        par3.yaxis.label.set_color(p4.get_color())

        plt.savefig("pyplot_multiple_y-axis.png", bbox_inches='tight')
        plt.title(("L16 temeperature characterization. Serial:%s" % serial))
        plt.tight_layout()



    def show_plot(self):
        print "showing the plot"
        plt.show()

    def main_func(self, duration, iterations, capture_type_mode, power_mode, use_capture):
        # TODO add try except
        self.data_set = {}
        #duration = 0
        iterations = int(iterations)
        # run by iteration rutine
        while iterations > 0:
            results = []
            # results.append(camera.capture_LCC())
            results.append(self.DUT.read_SOC_temperature())  # 1 Order should not be mixed
            results.append(self.DUT.read_asic_temp())  # 2
            results.append(self.DUT.read_current())  # 3
            results.append(self.DUT.read_voltage())  # 4
            current_time = self.DUT.get_local_time()
            print "results", results
            self.data_set[current_time] = results

            time.sleep(2)  # in real run change it to every 30 minutes
            iterations -= 1
            print "currently run ", iterations

        while

        self.plotting(self.data_set, self.DUT.get_sys_info()["dev_serial"])
        print "data set",  self.data_set

class Thermal_Run_GUI():
    def __init__(self, master):
        self.var = IntVar()
        self.ASICs_gr=IntVar()
        self.cont_cap_val = IntVar()
        self.standby_wake= IntVar()
        self.entrytext= StringVar()
        self.curent_status_var = StringVar()
        self.master = master
        master.title("L16 temp charachterization")
        self.DUT = L16()
        self.Execute=Execute()


        # self.cont_but_lbl = Label(master, text="Control buttons")
        # self.cont_but_lbl.grid(column =2,row=1)
        #TODO arange code by layout
        self.run_test = Button(master, text="Run", command=self.Execute.run_it)
        self.run_test.grid(column=1,row=2, pady=2, sticky=NW)

        self.run_test = Button(master, text="Export log file", command=self.Execute.export_data)
        self.run_test.grid(column=1, row=3, pady=2, sticky=NW)

        self.run_test = Button(master, text="Show Plot", command=self.Execute.show_plot)
        self.run_test.grid(column=1, row=4, pady=2, sticky=W)

        self.run_test = Button(master, text="STOP", command=self.Execute.export_data)
        self.run_test.grid(column=1, row=5, pady=2, sticky=W)

        self.run_type_lbl = Label(master, text="Run type: Time, Iteration")
        self.run_type_lbl.grid(column = 2, row=1, sticky=W)

        self.curent_status = Label(master, textvariable=self.curent_status_var)
        self.curent_status_var.set("Current test status: IDLE")

        self.curent_status.grid(column=3, row=1)

        time_but = Radiobutton(master, text="By time", variable=self.var, value=1).grid(column=2, row=2, sticky=W)
        iter_but= Radiobutton(master, text="By iteration", variable=self.var, value=2).grid(column=2, row=2, sticky=E)

        cont_capture = Checkbutton(master, text="Continues capture", variable=self.cont_cap_val)
        cont_capture.grid(column=2, row=10, sticky=W)


        self.iteration_or_time = Entry(master, textvariable=self.entrytext)
        self.iteration_or_time.insert(0,"") # make sure entry field is clean
        self.iteration_or_time.grid(column=2, row=3, sticky=N, padx=10)

        capture_asics = Label(master, text="Asics will be used")
        capture_asics.grid(column=2, row=6, sticky=W)

        c = Radiobutton(master, text="ASIC 1,2", variable=self.ASICs_gr,value = 1)
        c.grid(column=3, row=6,sticky=W)

        c = Radiobutton(master, text="ASIC 1,2,3", variable=self.ASICs_gr,value = 2)
        c.grid(column=4, row=6, sticky=W)

        self.run_type_lbl = Label(master, text="Force Wake/Sleep mode")
        self.run_type_lbl.grid(column=2, row=7, sticky=W)

        stan_but = Radiobutton(master, text="Force stanby?", variable=self.standby_wake, value=1)
        stan_but.grid(column=2, row=9, sticky=W)

        awake_but = Radiobutton(master, text="Keep awake?", variable=self.standby_wake, value=2)
        awake_but.grid(column=3, row=9, sticky=W)



root = Tk()
L16_GUI = Thermal_Run_GUI(root)
#L16_GUI(root)
#print my_gui.X
root.mainloop()

#TODO separate gui from run to diff files

# ex= Execute
# ex.run_it()





