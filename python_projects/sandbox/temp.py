"""
def reverse(string):
    if len(string) < 2:
        return string
    else:
        return reverse()

def convert(numb, base):
    string = "0123456789ABCDEF"
    if numb < base:
        return string[numb]

    else:
        return (convert(numb//base, base)) + string[numb%base]

print convert(10, 2)
"""


def reverse(s):
    if s == "":
        return s
    else:
        return s[-1] + reverse(s[:-1])
#print reverse("Go hang a salami Im a lasagna hog")

def removeWhite(s):
    new_sent = ""
    list = s.split()
    for i in list:
       new_sent = new_sent + i.strip() + " "
    new_sent  = new_sent.strip()
    return new_sent

#print removeWhite("madam i'm adam")

import turtle
def tree(branchLen,t):
    if branchLen > 5:
        t.forward(branchLen)
        t.right(20)
        tree(branchLen - 15, t)
        t.left(40)
        tree(branchLen - 10, t)
        t.right(20)
        t.backward(branchLen)

#t = turtle.Turtle()
#tree(20, t)
def exp():
    print 'some errors'

def a():
    try:
        a = a+ ""

    except:
        exp()



a()
