from Tkinter import Frame, Button
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
matplotlib.use("TkAgg")
import Tkinter as tk


class measure_gui(Frame):
    res_data_set = []
    cycle_list = []

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.init_val = 1
        self.but_run = Button(master, text="Run", command=self.main)
        self.but_run.pack()
        self.but_show = Button(master, text="Show plot", command=self.execut)
        self.but_show.pack()
        self.but_res = Button(master, text="Reset", command=self.reset)
        self.but_res.pack()

    def main(self):
        print "Gui is starting"

    def execut(self):
        f = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        a.plot(self.cycle_list, self.res_data_set)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def reset(self):
        self.res_data_set = [1, 1, 1, 1, 1, 1, 1]
        self.cycle_list = [7,6,5,4,3,2,1]

my_app = measure_gui()

my_app.res_data_set = [1,2,3,4,5]
my_app.cycle_list= [6,7,8,9,20]
my_app.mainloop()