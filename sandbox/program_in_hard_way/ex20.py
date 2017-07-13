from sys import argv
script, input_file = argv

def print_all(f):
    print "redading", f.read()

def rewind(f):
    f.seek(0) # moves pointer to the begining of the file

def print_a_line(line_count,f):
    print "readingf a line",line_count, f.readline() # every time, as long as file open it will read a line and stops there,
    # in next call it will continue from where its left

current_file = open(input_file)

print "First let's print the whole file:\n"

print_all(current_file)

print "Now let's rewind, kind of like a tape."
rewind(current_file)

print "Let's print three line:"

current_line =1
print_a_line(current_line, current_file)

current_line = current_line +1
print_a_line(current_line, current_file)

current_line = current_line +1
print_a_line(current_line, current_file)

print #######################################
print "testing to see can it print any other lines?"
current_line = current_line +1
print_a_line(current_line, current_file)

print "any more lines?"

current_line = current_line +1
print_a_line(current_line, current_file)


print "now closing the file"
current_file.close()
print "File is closed"
print "###################################################"

print """starting over
over
over
#####

opening the file again
"""

current_file = open(input_file)
current_line =  0
print "file has been opened, lets read"

current_line = current_line +1
print_a_line(current_line, current_file)

print "DONE"

"""
conclusions:
1. readline will not return new line character on both python versions
2. file.seek() will return pointer to nuber of bytes indicated..
3. after pointer reaches to the end of file as longs as file open, it will not return anythins else
4. if we reopen the file again it will start read form begining
"""