import tkinter as tk
from tkinter import filedialog
import os

application_window = tk.Tk()

#build a list of tuples foe each file type the file dialog should display
my_filetype = [('all files', '.*'), ('text files', '.txt')]

#ask user to select a folder

answer = filedialog.askdirectory(parent=application_window, initialdir = os.getcwd(), title = "Please select a folder:")

#ask user to select a file
answer = filedialog.askopenfilename(parent=application_window, initialdir=os.getcwd(), title = "Please select a file:", filetypes = my_filetypes)

#ask the user to select a one or more names
answer = filedialog.askopenfilenames(paren=application_window, initialdir= os.getcwd(), title = "Please select one or more files", filetypes = my_filetypes)

#ask the user to select a single file name for saving.
answer = filedialog.asksaveasfilename(parent=application_window, initialdir=os.getcw(), title = "Please select file name for saving", filetypes = my_filetypes)
