import Tkinter as tk, tkFileDialog


class Example(tk.Frame):
    eventsdb = "empthy"

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        open_button = tk.Button(text='save', command=self.save_events_db)
        print_button = tk.Button(text='Print DB', command=self.print_value)

        open_button.pack(fill=tk.X)
        print_button.pack(fill=tk.X)

    def save_events_db(self):
        #file_path_string = tkFileDialog.askopenfilename()
        self.eventsdb = "test text"

    def print_value(self):
        print self.eventsdb





root=tk.Tk()
Example(root).pack(fill="both", expand=True)
print Example.eventsdb
Example.eventsdb = "new_text"
print Example.eventsdb
root.mainloop()
