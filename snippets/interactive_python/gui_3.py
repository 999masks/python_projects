import tkinter as tk
from tkinter import simpledialog

application_window = tk.Tk()

answer = simpledialog.askstring("Input", "some string", parent = application_window)

if answer is not None:
	print ("Your first name is, ", answer)
else:
	print ("You done have first name")
	

answer = simpledialog.askinteger("Input", "what is your age", parent = application_window, minvalue =0, maxvalue=100)

if answer is not None:
	print ("Your age is :", answer)
else:
	print ("You dont have an age?")
	
answer = simpledialog.askfloat("Input", "what is your salary", parent= application_window, minvalue = 0.0, maxvalue = 10000.0)

if answer is not None:
	print ("Your salary is ", answer )
else:
	print ("You donr have a salary")


	
