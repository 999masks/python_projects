from matplotlib import pyplot as plt
from matplotlib.artist import setp

from time import strftime, localtime
import os
import time
import sys

def export_data(data_set):
    file_path = os.path.join(os.environ["HOMEPATH"], os.path.join("Desktop", "L16_temp_characterization_%s.csv" % (
        strftime("%Y_%m_%d", localtime()))))
    # print file_path
    rep_file_obj = open(file_path, "w")
    top_row = (
        "Time,SOC temperature, CCB temperature, Battery current, Battery voltage, Battery Capacity, Is charging\r")
    rep_file_obj.write(top_row)

    for rows in data_set.items():
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

def run_it():
    run_by_time = self.var.get()
    entry_data = int(self.iteration_or_time.get())
    zoom_level = self.ASICs_gr.get()
    power_mode = self.standby_wake.get()
    cont_cap = self.cont_cap_val.get()
    if run_by_time == 1:
        iterations = entry_data
        duration = None
    elif run_by_time == 2:
        duration = entry_data
        iterations = None
    else:
        sys.exit("Please check that all field is checked")

    self.curent_status_var.set("Current status: RUNNING")
    #camera = L16()

def read_all_fields(self):
    print "By time", self.var.get()  # good 0 - unchecked,1,2
    # print "By iteration",
    print "entry field", self.iteration_or_time.get()  # good
    print "Asic 1,2", self.ASICs_gr.get()  # good
    # print "Asic 23",
    print "Force stanby", self.standby_wake.get()  # good 0 - unchecked,1,2
    # print "keep awake",
    print "continious capture", self.cont_cap_val.get()  # good 0,1

def plotting(data_set, serial):
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

    def main_func(duration, iterations=None, capture_type_mode=None, extra_param=None):
        data_set = {}
        duration = 0
        while iterations > 0:
            results = []
            # results.append(camera.capture_LCC())
            results.append(camera.read_SOC_temperature())  # 1 Order should not be mixed
            results.append(camera.read_asic_temp())  # 2
            results.append(camera.read_current())  # 3
            results.append(camera.read_voltage())  # 4
            current_time = camera.get_local_time()
            data_set[current_time] = results

            time.sleep(5)
            iterations -= 1
            print "currently run ", iterations

        print data_set

        export_data(data_set)
        plotting(data_set, camera.get_sys_info()["dev_serial"])
        plt.show()
