def inttostring(integr, base):
    string = "0123456789ABCDEF"
    if integr < base:
        return string[integr]
    else:
        return inttostring(integr // base, base) + string[integr%base]


print (inttostring(10, 2))


"""
    1. abc // base rem1
    2. ab // base rem2
    3. a // base rem 3
    return string[rem1j] + string[rem2] + string[rem3]

00000000000000000000000000001011
"""