from Tkinter import Frame, Button
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
matplotlib.use("TkAgg")
import Tkinter as tk
#import ttk



class measure_gui(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.init_val = 1
        self.but = Button(master, text="Run", command=self.execut)
        self.but.pack()

    def execut(self):
        f = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        a.plot(plot_data_a, plot_data_b)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

plot_data_a= [1, 2, 3, 4, 5, 6, 7, 8]
plot_data_b = [5, 6, 1, 3, 8, 9, 3, 5]
app = measure_gui()
#app.execut(plot_data)
app.mainloop()