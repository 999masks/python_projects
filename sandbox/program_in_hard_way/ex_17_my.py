from sys import argv
from os.path import exists

script_file, in_file, out_file = argv


print "does input file exist? %s, does output file exist? %s"%(exists(in_file), exists(out_file))

in_file_obj = open(in_file, "r+")
out_file_obj = open(out_file,"w+" )
raw_input("Are you ready to copy, hit enter if Yes?")

in_file_data = in_file_obj.read()
print in_file_data
print "OK, we are copying from one file to another"

line_num = 0
out_file_obj.write(in_file_data)
line_num +=1
#print "%d line has benn written"%(line_num)
in_file_obj.close()
out_file_obj.close()
print "are these files are closed? infile ? %s , out_file ? %s"% (in_file_obj.closed, out_file_obj.closed)
raw_input("Hit enter if you want to take a look to new file, otherwise hit CTRL+C to cancell")

out_file_obj = open(out_file, "r")
print out_file_obj.readlines()
out_file_obj.close()

