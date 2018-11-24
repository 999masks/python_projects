import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

messagebox.showinfo("info")
messagebox.showerror("error")
messagebox.showwarning("warninings")

answer = messagebox.askokcancel("question Do ypu want to open this?")
answer = messagebox.askretryacamcel("Question", "Do you want to try that again")
answer  = messagebox.askkyesnocancel("Question, Continue playing")


window = tk.Tk()


window.mainloop()