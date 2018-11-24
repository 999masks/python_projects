##############################################
# Ligh L16 temp characterization program
# current version V0.14_1
# V 0.6
# created by Mamo 11/01/2017
# Light.co
# ..............
# ..............
# ..............
# V 0.7 changelog
## 1. added timing control on most function dealing with camere keyevents
## 2. added time stamp
## 3. idle time counter on terminal
# V 0.8 changelog
## adding avg power consumtion durring active cycle- pending
## now it dynamically calculates run time and adjust next idle time to finish on time
## added average power reading
## add asic and snap error log export file, based on keywords
## test to string test data before creating a pllot
# V 0.13
# # Fixed issues with plotting (when not digit appear on data set)
# V 0.14
## Added option preview mode as active mode
## revised polotting
## added automatic export feauture after each run





# import run_character
from Tkinter import Tk, Label, Button, Entry, IntVar, END, W,E,S,N,NW, StringVar, Radiobutton, Checkbutton, DISABLED
import sys
#from adbandroid import adb_android

from matplotlib import pyplot as plt
from matplotlib.artist import setp

from threading import *
import threading

from time import strftime, localtime
import os
import time, datetime
import sys

try:
    from L16 import *
except:
    sys.exit("L16 not loaded")
# TODO avoid using class variables
# TODO move class variables under init, it will create separate variable after each object initialization
# TODO match colors in plot with legend -DONE
# TODO fiX fix run by time and run by iteration timing issues
# TODO fix GUI freezing issues -DONE
# TODO move wait time the end
# TODO add current timeout status for user
# TODO add temperature parameter from entry data as column in log file -DONE
# TODO add average power measurement durring active cycle -DONE
# TODO revise remanin idle time calculation
# TODO redirect stdOut to to tkinter window
# TODO implement watchdog, to close after timeout exceeded
# TODO keep unit always charging when on idle, later add this as option
# TODO save filenames with serial, to avoid owerwrite if multiple units are connected

#debug = True
debug = False

if debug:
    print "Debugging enabled"

# class run_as_thread(threading.Thread):
#
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.do_run = True
#
#     def run(self):
#         while self.do_run:
#             pass
#
#     def stop_thread(self):
#         self.do_run = False
#
# timer = run_as_thread

class Execute():
    def __init__(self):
        L16.dev_list = []
        self.after_id = None
        self.data_set = {}
        self.SOC_errors = []
        self.ASIC_errors = []
        self.is_errors = None
        self.run_status = True
        self.total_time = 0
        self.stop = False
        self.finish = False

        try:
            L16.adb_obj = adb_android
            self.DUT = L16()
            self.DUT.adb_obj.start_server()
            self.DUT.connect()
            self.serial = self.DUT.get_sys_info()["dev_serial"]
            self.DUT.startLightapp()
            self.file_path = os.path.join(os.environ["HOMEPATH"], os.path.join("Desktop", "L16_temp_characterization_%s_%s" %(
                strftime("%Y_%m_%d", localtime()), self.serial)))
        except:
            sys.exit("No device found")

    def reset_routine(self):
        print "Resetting entry fields"
        self.run_mode = None
        self.iteration_sequence_list = None
        self.zoom_level = None
        self.display_always_on = None
        self.cont_cap_prev_only = None
        self.charging_enabled = None
        self.total_time = 0
        self.set_total_pause = 0
        self.real_total_pause = 0
        self.cycle_active_duration = 0
        self.accum_active_duration =0
        self.end_cap_time = 0
        self.after_id = True
        self.iterations = 0
        self.duration = 0

    def read_fields(self): # this will read all the inputs and apsses to main function
        self.after_id = True
        if debug:
            print "Removing old data..."
        self.reset_routine()
        try:
            self.run_mode = L16_GUI.var.get()
            self.entry_data = L16_GUI.iteration_or_time.get() # how long or how many iterations?
            self.zoom_level = L16_GUI.ASICs_gr.get() # will determine which ASIC group will be used
            self.display_always_on = L16_GUI.standby_wake.get()
            self.cont_cap_prev_only = L16_GUI.cont_cap_val.get()
            self.charging_enabled = L16_GUI.enable_charging_var.get()
            #print "display always on value", self.display_always_on
            print "I got this sequence", self.entry_data
            self.entry_data = self.entry_data.split(",")
            for item in self.entry_data:
                # print "item", item
                self.total_time = self.total_time + int((item.split(":")[-1]).split("p")[0])
            if len(self.entry_data)>0:
                    # TODO make sure that run mode is correct
                    self.iteration_sequence_list = (self.entry_data)
                    self.after_id = True # For rerun
                    self.run_status = True # For rerun
                    self.Gui_callback()
            elif len(self.entry_data) <1:
                print "Please make sure all fields are checked"
        except:
            raise
            sys.exit("Wrong data is entered. Exiting ...")

    def Gui_callback(self):
        # print "main func go called"
        if self.after_id:
                if self.run_status:
                    try:
                        # print "came to global tag"
                        self.tr = Thread(target = self.main,
                                         args=(self.run_mode,
                                               self.iteration_sequence_list,
                                               self.zoom_level,
                                               self.display_always_on,
                                               self.cont_cap_prev_only,
                                               self.charging_enabled))
                        self.tr.start()
                        self.run_status = False
                        # print "Thread started", tr.is_alive
                    except:
                        print "Error due to excecution. TR"
                self.after_id = root.after(100, self.Gui_callback)
        elif not self.after_id:
            #self.tr.join()
            print "Got stop. Please wait until last cycle finishes"

    
    def main(self,
             run_mode,
             iteration_sequence_list,
             zoom_level,
             display_always_off,
             cont_cap__prev_only,
             charging_enabled):

        """
        :param run_mode: run
        :param iteration_sequence_list:
        :param zoom_level:
        :param display_always_off:
        :param cont_cap__prev_only:
        :return:
         1.capture mode rutines moved inside wake up loop, with parameters
         2. run mode disabled to benetfit sequentioal run
        """
        test_start_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print "Test started at ", test_start_time
        #self.after_id = True
        self.data_set = {}
        if charging_enabled ==1:
            charging_enabled = True
        else:
            charging_enabled = False
        #print "charging state", charging_enabled

        if display_always_off == 1:
            display_always_off = True
        else:
            display_always_off = False
        print "Total duration is: %s minutes\n" % self.total_time
        #estim_end_time = test_start_time
        print "Charging enabled? %s"%charging_enabled
        self.DUT.charge_enabled(charging_enabled)
        if debug:
            print "Removing files from storage..."
        print "Files have been removed?: %s" % self.DUT.remove_files()
        #print "Data set i got ", (run_mode, iteration_sequence_list,zoom_level, display_always_off, cont_cap__prev_only, charging_enabled)
        while self.after_id and not self.stop and not self.finish:
            #print "start whiloop,after id and stop status", self.after_id, self.stop, self.finish
            adj_idle_pause=60
            for item in iteration_sequence_list:
                #print "Total esosors reading duration is ", self.accum_active_duration
                self.results = []
                print "item", item, "time", strftime("%H:%M:%S", localtime())
                temp_tag, time_set = item.split(":")  # pause time in minutes
                if "p" in time_set.lower():
                    pause  = int(str(time_set[:-1]))  # in minutes
                    idle = True
                    # Calculating idle time based on previos run time delay
                    print "current pause {}, set_total_pause {}, sensor reading duration {}".format(pause*60, self.set_total_pause, self.accum_active_duration)
                    adj_idle_pause = (pause * 60) + (self.set_total_pause - self.accum_active_duration)
                    if adj_idle_pause < 0:
#                         if iteration_sequence_list[iteration_sequence_list.index(item)+1]:
#                             # adjusting next idle if existing idle less than adjustment
#                             iteration_sequence_list[iteration_sequence_list.index(item) + 1]= int(iteration_sequence_list[iteration_sequence_list.index(item)+1]
# )+adj_idle_pause
                        adj_idle_pause = 0

                    print "self.set_total_pause", self.set_total_pause
                    #print "sensor reading duration", self.cycle_active_duration
                    print "Total pause has been adjusted: %d seconds"%adj_idle_pause
                    self.accum_active_duration = 0
                    if debug:
                        print "zeroing sensor duration"
                else:
                    pause = int(time_set)
                    idle = False
                    self.real_total_pause = 0
                    self.set_total_pause = 0

                #print "Total duration is: %s minutes"%self.total_time
                cycle_pause_sec = 60 # will adjust accordin run speed 1 min

                total_cycle_time = 0
                self.set_total_pause = pause*60
                while pause > 0 and self.after_id and not self.stop:
                    print "Remaining pause {} minutes".format(pause)
                    if not idle:
                        run_time_start = time.time()

                        self.DUT.charge_enabled(charging_enabled)
                        print "charging enabled ? ", charging_enabled
                        if cont_cap__prev_only == 1: # continues capture
                            start_cap_time = time.time()
                            volt_curr_cap = self.DUT.wakeup_or_run(cycle_pause_sec, cont_cap__prev_only, zoom_level)
                            self.end_cap_time = time.time() - start_cap_time
                            if not display_always_off:
                                self.DUT.wakeup_or_run(0) # single run at the end
                            else:
                                print "Forcing to sleep"
                                #start_force_sleep_time = time.time()
                                self.DUT.force_sleep(0)
                                #end_force_sleep_time = time.time() - start_force_sleep_time
                                #print "it takes times for sleep", end_force_sleep_time
                            pause -= 1  # Cycle ends
                            #print "%d minutes remaining for current cycle"%pause
                            self.total_time -= 1
                            print "%d minutes to finish" % (self.total_time)

                        elif cont_cap__prev_only == 2: # preview
                            print "Preview only mode selected"
                            volt_curr_cap = self.DUT.wakeup_or_run(cycle_pause_sec, cont_cap__prev_only, zoom_level)
                            pause = pause -1  # Cycle ends

                        elif cont_cap__prev_only == 0: # default no capture
                            #print "No capture"
                            if not display_always_off:
                                #print "display will be On"
                                self.DUT.wakeup_or_run(cycle_pause_sec)
                            elif display_always_off:
                                print "display will be off"
                                self.DUT.force_sleep(0)
                                time.sleep(cycle_pause_sec)
                            pause = pause -1  # Cycle ends


                        # Collecting SOC_errors
                        SOC_error_lines = self.DUT.parse_SOC_fatal_errors()
                        if "error" in str(SOC_error_lines).lower():
                            self.is_errors = "Errors"
                        else:
                            self.is_errors = "No Errors"
                        self.SOC_errors = self.SOC_errors + SOC_error_lines

                        ASIC_error_lines = self.DUT.parse_ASIC_fatal_errors()
                        if "error" in str(ASIC_error_lines).lower():
                            self.is_errors = "Errors"
                        else:
                            self.is_errors = "No Errors"
                        self.ASIC_errors = self.ASIC_errors + ASIC_error_lines

                        run_time_stop = time.time()

                        each_cycle_dur = int(run_time_stop - run_time_start)
                        self.real_total_pause = self.real_total_pause + each_cycle_dur

                        non_idle_end = time.time()
                        total_non_idle_duration = non_idle_end - run_time_start
                        print "total capture duration", total_non_idle_duration

                        print "%d minutes remaining for current cycle" % pause
                        self.total_time -= 1
                        print "%d minutes to finish" % (self.total_time)

                        self.cycle_active_duration = (time.time() - run_time_start)
                        self.accum_active_duration = self.accum_active_duration + self.cycle_active_duration
                        self.cycle_active_duration = 0

                    elif idle:
                        # will stay here entire cycle pause
                        print "Idling... Charging the unit"
                        self.DUT.charge_enabled(True)
                        start_idle_time = time.time()
                        if display_always_off:
                            if debug:
                                print "Display stays off"
                            self.DUT.force_sleep()
                            while adj_idle_pause>=1:
                                #print "%d seconds remainig for idle.."%adj_idle_pause
                                time.sleep(1) # adjustment , normally it take more that
                                adj_idle_pause -=1
                                # if new_idle == adj_idle_pause - 60:
                                #     print "60"
                        elif not display_always_off:
                            print "Display stays on"
                            self.DUT.wake_up(adj_idle_pause)
                        print  "it takes %f seconds to pause"%(time.time() - start_idle_time)

                        pause = None  # Cycle ends
                        self.total_time = self.total_time -int(round(adj_idle_pause/60))
                        print "%d minutes to finish" % (self.total_time)
                        if debug:
                            print "Resseting idle time"
                        adj_idle_pause = 60
                    else:
                        print "something went wrong in MAIN loop"

                    if not self.DUT.batteryCharged():
                        self.after_id = False
                        #self.tr.join()
                        print "Battery is critical, test interrupted"
                        # print "The end of loop"


                if not idle:
                    start_sensor_reading_time = time.time()
                    # Order should not be mixed
                    # Target temperature run tag #1
                    self.results.append(str(temp_tag))

                    # SOC temperature #2
                    self.results.append(self.DUT.read_SOC_temperature())

                    # ASIC1 temperature #3
                    self.results.append(self.DUT.read_asic_log_temp_())

                    # ASIC temperature from kernel #4
                    self.results.append(self.DUT.read_asic_temp_kernel())

                    # Current reading #5
                    current_read = self.DUT.read_current()
                    self.results.append(current_read)

                    # Voltage reading #6
                    self.results.append(self.DUT.read_voltage())

                    # Battery level #7
                    battery_level = (self.DUT.batteryCharged())
                    self.results.append(battery_level)
                    print "Battery {}% charged".format(battery_level)

                    # Charging/Discharging #8
                    if "-" in str(current_read):
                        self.results.append("Charging")
                    elif float(current_read) == 0:
                        self.results.append("0 Current")
                    else:
                        self.results.append("Discharging")

                    # Power mode routine, column #9
                    # True bacause run mode has disabled

                    if display_always_off:
                        self.results.append("Force standby")
                    else:
                        self.results.append("Keep awake")

                    # Capture mode routine, column #10
                    if cont_cap__prev_only == 1:
                        self.results.append("Capturing every %d seconds" % int(5))
                    elif cont_cap__prev_only == 2:
                        self.results.append("Preview only")
                        print "No capture during run"

                    elif cont_cap__prev_only == 0:
                        self.results.append("No capture")
                        print "No capture during run"

                    # zoom level  routine, asic 1,2 or all asics, column #11
                    if zoom_level == 0:
                        self.results.append("No ASIC is used")
                    elif zoom_level == 1:
                        self.results.append("ASIC 1 and 2")
                    elif zoom_level == 2:
                        self.results.append("All ASICs")
                    else:
                        print "Zoom level got uknoown input -", zoom_level
                        self.results.append("Used default A1,2")

                    # power consumption
                    if volt_curr_cap:
                        avg_volt = float(sum(volt_curr_cap[0]) / len(volt_curr_cap[0]))
                        avg_curr = float(sum(volt_curr_cap[1]) / len(volt_curr_cap[1]))
                        avg_power = avg_curr * avg_volt
                    else:
                        avg_power = 0
                        print "No power data is available"
                    self.results.append(avg_power)

                    if debug:
                        print "avg_volt", volt_curr_cap[1], len((volt_curr_cap[1]))
                        print "avg current", volt_curr_cap[0], len(volt_curr_cap[0])


                    if self.results and len(self.results) > 0:
                        current_time = self.DUT.get_local_time()
                        self.data_set[current_time] = self.results
                        self.results = []

                    ## Power consumption calculation based on list minute capture iteration # 12
                    print "calculating power consumption, based on last iteration..."




                    end_sensor_reading_time = time.time()
                    sensor_reading_duration = end_sensor_reading_time-start_sensor_reading_time
                    if debug:
                        print "average power concumtion is :", avg_power
                        print "sensor reading time is", sensor_reading_duration
                    self.accum_active_duration = self.accum_active_duration + sensor_reading_duration
                    sensor_reading_duration = 0

                    print "Total active duration is so far ", self.accum_active_duration
                    self.export_data()


            test_end_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            print "Test has been ended at:", test_end_time
            print "Test done with %s" % self.is_errors
            #print "Test took %d minutes",  "{:0>8}".format(datetime.timedelta((time.time() - Test_has_started)))
            self.finish = True
            print "Putting device on charge..."
            self.DUT.charge_enabled(True)
            self.reset_routine()
            print "Forcing unit to Stand BY...\n \n"
            self.DUT.force_sleep()
            self.export_data()

    def export_data(self):
        #print self.file_path
        #self.file_path = "C:\\Users\\mamo\\Desktop\\abc"
        rep_file_obj = open(("C:"+self.file_path +".csv"), "w")
        self.SOC_error_log_file_obj = open(("C:"+self.file_path + "_SOC_error.log"), "w")
        self.ASIC_error_log_file_obj = open(("C:"+self.file_path + "_ASIC1_error.log"), "w")
        top_row = (
            "Time,Set temperature(1),SOC temperature(2),ASIC temperature(3),ASIC temperature from kernel(4),Battery current(5),Battery voltage(6),Battery Capacity(7),Is charging(8),Power mode(9),Capture mode(10),ASIC group(11),Power dur.capture W(12)\n")
        rep_file_obj.write(top_row)
        dic_items = self.data_set.items()
        dic_items.sort()
        for rows in dic_items:
            # print "current row", rows
            # temp_row = ""
            temp_row = str(rows[0])
            # print temp_row
            for data in rows[1]:
                # print "str values", str(data)
                temp_row = str(temp_row) + "," + str(data)
                # print "temp_row mod", temp_row
            rep_file_obj.write((temp_row + "\n"))
        rep_file_obj.close()

        # print "SOC_errors", self.SOC_errors
        for lines in self.SOC_errors:
            #if debug:
                #print "error_lines", lines
            self.SOC_error_log_file_obj.write(lines)
        self.SOC_error_log_file_obj.close()

        for lines in self.ASIC_errors:
            # print "error_lines", lines
            self.ASIC_error_log_file_obj.write(lines)
        self.ASIC_error_log_file_obj.close()

        print "Files successfully been exported to Desktop"

    def plotting(self, data_set, serial):
        if debug:
            print "Data set", data_set
        x_1 = range(1, (data_set.__len__() + 1))
        x_target_temp = []
        y_SOC_temp = []
        y_power_cons = []
        y_asic_temp = []
        y_asic_temp_kern = []
        y_current = []
        x_labels = []
        x_labels_1 = []
        for time_st in sorted(data_set.keys()):
            x_labels.append((time_st)+" TMP:"+ data_set[time_st][0]) # adding set snippets to the X axis - timestamp

        for time_st in sorted(data_set.keys()):
            x_labels_1.append((time_st))

        for item in x_labels_1:
            #print "item", item
            try:
                _tt = float(data_set[item][0])
                x_target_temp.append(str(_tt))
            except:
                x_target_temp.append(0)
            #print "1", (data_set[item][0])

            try:
                _St = float(data_set[item][1])
                y_SOC_temp.append(str(_St))
            except:
                y_SOC_temp.append(0)
            #print "2", (data_set[item][1])

            try:
                _at = float(data_set[item][2])
                y_asic_temp.append(str(_at))
            except:
                y_asic_temp.append(0)
            #print "3", (data_set[item][2])

            try:
                _AT = float(data_set[item][3])
                y_asic_temp_kern.append(str(_AT))
            except:
                y_asic_temp_kern.append(0)
            #print "4", (data_set[item][3])

            try:
                _c = float(data_set[item][4])
                y_current.append(str(_c))
            except:
                y_current.append(0)
            #print "5", (data_set[item][4])

            try:
                _v =float(data_set[item][10])
                y_power_cons.append(str(_v))
            except:
                y_power_cons.append(0)
            #print "6", _v
            if debug:
                print x_labels, x_target_temp, y_SOC_temp, y_asic_temp, y_current, y_power_cons

        fig = plt.figure()
        host = fig.add_subplot(111)

        par1 = host.twinx()
        par2 = host.twinx()
        par3 = host.twinx()

        host.set_xlabel("Time, target Temp. C")
        host.set_ylabel("Temperature C")
        par1.set_ylabel("ASIC1 tempereature C")
        par2.set_ylabel("Bat. Current A")
        par3.set_ylabel("Avg. Power W")

        host.set_ylim(-20,100)  # core
        #par1.set_ylim(-20,100)  # CCB
        par2.set_ylim(-2,5)  # current
        par3.set_ylim(-2,5)  # voltage

        color1 = plt.cm.viridis(2)
        color2 = plt.cm.magma(0.5)
        color3 = plt.cm.plasma(1)
        color4 = plt.cm.inferno(.7)

        plt.xticks(x_1, x_labels)
        setp(host.get_xticklabels(), rotation=90)  # rotate time label

        p, = host.plot(x_1, y_SOC_temp, color=color1, label="SOC Temp")
        p1, = par1.plot(x_1, y_asic_temp, color=color2, label="CCB Temp")
        p2, = par2.plot(x_1, y_current, color=color3, label="Bat. Current")
        p3, = par3.plot(x_1, y_power_cons, color=color4, label="Avg. power W")

        # legend in chart
        lns = [p, p1, p2, p3]
        host.legend(handles=lns, loc='best')

        # right, left, top, bottom
        par1.spines['left'].set_position(('outward', 20))
        #par2.spines['right'].set_position(('outward', 40))


        host.yaxis.label.set_color(p.get_color())  # correct
        par1.yaxis.label.set_color(p1.get_color())
        par2.yaxis.label.set_color(p2.get_color())
        par3.yaxis.label.set_color(p3.get_color())

        plt.savefig("pyplot_multiple_y-axis.png", bbox_inches='tight')
        plt.title(("L16 temeperature characterization. Serial:%s" % serial))
        plt.tight_layout()

    def show_plot(self):
        self.plotting(self.data_set, self.DUT.get_sys_info()["dev_serial"])
        # print "data set", self.data_set
        print "showing the plot"
        plt.show()


    def stop_job(self):
        print "Stop"
        self.after_id = False
        self.tr.join()
        self.run_status = False
        self.stop = True
        #root.after_idle()



        # if self.after_id:
    #     Thermal_Run_GUI.curent_status_var.set("Current status: RUNNING")
    # else:
    #     Thermal_Run_GUI.curent_status_var.set("Current status: Idle")


class Thermal_Run_GUI():
    def __init__(self, master):
        self.var = IntVar()
        self.ASICs_gr=IntVar()
        self.cont_cap_val = IntVar()
        self.enable_charging_var = IntVar()
        self.enable_charging_var.set(0)
        self.standby_wake= IntVar()
        self.entrytext= StringVar()
        self.curent_status_var = StringVar()
        self.master = master
        master.title("L16 snippets characterization")
        self.DUT = L16()
        self.Execute=Execute()
        self.remaining_time = self.Execute.total_time
        #self.iteration_variable = 0


        # self.cont_but_lbl = Label(master, text="Control buttons")
        # self.cont_but_lbl.grid(column =2,row=1)
        # TODO arange code by layout
        self.run_test = Button(master, text="Run", command=self.Execute.read_fields)
        self.run_test.grid(column=1,row=2, pady=2, sticky=NW)

        self.run_test = Button(master, text="Export results", command=self.Execute.export_data)
        self.run_test.grid(column=1, row=3, pady=2, sticky=NW)

        self.run_test = Button(master, text="Show Plot", command=self.Execute.show_plot)
        self.run_test.grid(column=1, row=4, pady=2, sticky=W)

        self.run_test = Button(master, text="STOP", command=self.Execute.stop_job)
        self.run_test.grid(column=1, row=5, pady=2, sticky=W)

        self.run_type_lbl = Label(master, text="Run type: Sequence")
        self.run_type_lbl.grid(column = 2, row=1, sticky=W)

        self.curent_status = Label(master, textvariable=self.curent_status_var)
        self.curent_status_var.set("Currently ramaining %d cycles"%self.remaining_time)
        self.curent_status.grid(column=3, row=1)


        self.entry_values = Label(master, text="Please input target temperature, duration(min.)\n add 'p' for idle next to it. EX: 25:60p,25:5,-10:40p,-10:5")
        self.entry_values.grid(column=3, row=3)

        # time_but = Radiobutton(master, text="By time", variable=self.var, value=1).grid(column=2, row=2, sticky=W)
        # iter_but= Radiobutton(master, text="By iteration", variable=self.var, value=2).grid(column=2, row=2, sticky=E)

        cont_capture = Radiobutton(master, text="Continues capture", variable=self.cont_cap_val, value = 1)
        cont_capture.grid(column=2, row=10, sticky=W)

        preview_but = Radiobutton(master, text="Preview only", variable=self.cont_cap_val, value = 2)
        preview_but.grid(column=3, row=10, sticky=W)

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

        stan_but = Radiobutton(master, text="Force standby?", variable=self.standby_wake, value=1)
        stan_but.grid(column=2, row=9, sticky=W)

        awake_but = Radiobutton(master, text="Keep awake?", variable=self.standby_wake, value=2)
        awake_but.grid(column=3, row=9, sticky=W)

        enable_charging_check = Checkbutton(master, text="Enable charging", variable=self.enable_charging_var)
        enable_charging_check.grid(column=2, row=2, sticky=W)






root = Tk()
L16_GUI = Thermal_Run_GUI(root)
# L16_GUI(root)
# print my_gui.X
root.mainloop()

# ex= Execute
# ex.read_fields()


if __name__ == "__main__":
    root.mainloop()


