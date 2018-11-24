

def reverse(a):
    if a == "":
        return a
    else:
        return  (a[-1]) + reverse(a[0:((len(a)-1))])





def reverseString(s):
    vr = len(s)-1
    new_str = ""
    while vr > -1:
        new_str = new_str + s[vr]
        vr = vr - 1

    return new_str

s = "a man"
#print reverseString(s)


def reverseString1(s):
    new_str = s[::-1]

    return new_str

s = "a man"
print reverseString1(s)