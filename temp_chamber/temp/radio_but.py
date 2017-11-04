from Tkinter import IntVar, Radiobutton, Label, Tk, W, StringVar, Button


class Temps:

    def __init__(self):
        #self.master = master
        self.var = IntVar()# must be instantiated after wodget has created
        Radiobutton(text="Option 1", variable=self.var, value=1, command=self.sel).pack(anchor=W)
        #self.but.pack(anchor=W)
        Radiobutton(text="Option 2", variable=self.var, value=4).pack(anchor=W)
        run = Button(text = "Run", command = self.sel).pack(anchor = W)

        self.label = Label()
        self.label.pack()

    def sel(self):
        selection = "You selected the option " + str(self.var.get())
        self.label.keys()
        self.label.config(text = selection)
        print selection

root = Tk()
my_radio = Temps()
root.mainloop()

"""
from Tkinter import *
def sel():
    selection = "You selected the option " + str(var.get())
    label.config(text = selection)
root = Tk()
var = IntVar()

Radiobutton(root, text="Option 1", variable=var, value=1, command=sel).pack(anchor=W)
Radiobutton(root, text="Option 2", variable=var, value=2, command=sel).pack(anchor=W)
Radiobutton(root, text="Option 3", variable=var, value=3, command=sel).pack(anchor=W)
label = Label(root)
label.pack()
"""




