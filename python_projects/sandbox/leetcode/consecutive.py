def consecutive_1(nums):
    #array = bin(array)

    #is_one = True
    list_of_max = []
    count = 0
    pos = 0
    for i in nums:
        if i == "1" and pos < len(nums):
            count +=1
        else:
            if count > 0:
                list_of_max.append(count)
                count = 0
        pos += 1
    if count > 0:
        list_of_max.append(count)
    #print list_of_max
    if len(list_of_max)> 0:
        return max(list_of_max)
    else:
        return 0



print consecutive_1("0")