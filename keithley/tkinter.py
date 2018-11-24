from Tkinter import Tk
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def myplotcode():
    x = np.linspace(0,2*np.pi)
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(x, x**2)

    return fig

class mygui(Tk.frame):
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent)
        self.parent = parent

        self.fig = myplotcode()
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.show()

        self.canvas.get_tk_widget().pack()
        self.pack(fill=Tk.BOTH, expand=1)

root = Tk.Tk()
app = mygui(root)

root.mainloop()