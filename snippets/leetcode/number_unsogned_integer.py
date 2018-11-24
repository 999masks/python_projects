# def haminglight(n):
#     string_list = "0123456789ABCD"
#     count = 0
#     num_type = 2
#     if n < num_type:
#         bits =  string_list[n]
#     else:
#         bits = haminglight(n // num_type) + string_list[(n%num_type)]
#
#     for i in bits:
#         if i == 1:
#             count += 1
#     return count
#
# print (haminglight(12460))

#
def hammingWeight(n):
    """
    :type n: int
    :rtype: int
    """
    print "n", bin(n), "n string", str(bin(n))
    count = 0
    n = str(n)
    for i in n:
        if i == str(1):
            count += 1
    return count


# def hammingWeight(n):
#     return str(bin(n)).count('1')


print hammingWeight("0000000000000100000000000000011")
