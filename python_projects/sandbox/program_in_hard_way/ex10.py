from sys import argv
file_name = argv
try:
    file_name, variable = argv
except:
    print "something went wrong"
tabby_cat = "\t I'm tabbed in."
persian_cat = "I'm split\non a line."
backslash_cat = "I'm \\ a \\cat."
fat_cat = """
I'll do a list:
\t* Cat food
\t* Fishies
\t* Catnip\n\t Grass
"""

print tabby_cat
print persian_cat
print backslash_cat
print fat_cat
print "this is the file name", file_name
#print "variable", variable
try:
    if variable is True:
        print "variable is ", variable
    else:
        print "wariable is not true"
except:
    print "There is no variable declared"

"""
conclusions:
if file executed with space after file name, python will
understand that it is an argument
if file execited with extra parameter, python will not
treat as True
"""



