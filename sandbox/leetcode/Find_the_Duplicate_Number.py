def findDuplicate(nums):
    ####################logic one#####################
    # if len(nums)>=3:
    #     maxim = max(nums)
    #     minim = min(nums)
    #     normal_list = range(minim, maxim+1)
    #     #print normal_list
    #     b = tuple(normal_list)
    #     print type(normal_list)
    #     for a_list in b:
    #         repeat = 0
    #         for b_list in nums:
    #             if a_list == b_list:
    #                 #print a_list
    #                 repeat +=1
    #             if repeat ==2:
    #
    #                 return a_list
    # else:
    #
    #     return 1
    #########################Logic second#########################
    """
    [3798,1, 46565, 6, 7, 886,4,57645879659,34567, 6, 465865, 3424, 444, 4224]
    :param nums:
    :return:


    :param nums:
    :return:

    int_list = []
    duplicates = []
    matches = 0
    if len(nums)>3:
        integers = [1,2,3,4,5,6,7,8,9,0]

        for i in integers:
            for dig_group in nums:
                #print dig_group
                string_dig = str(dig_group)
                pos = 0
                if str(i) == string_dig[pos]:
                    int_list.append(dig_group)
            if len(int_list) >1:
                int_list.sort() # sort in order to find lesser digit number
                duplicates.append(int_list)
                int_list = []
            int_list=[]

        # for dup_list in duplicates:
        #     end = len(str(dup_list[0]))
        #     possition = 0
        #     print dup_list
        #     while possition < end:
        #         if str((dup_list)[0])[possition] == str((dup_list)[-1])[possition]:
        #             possition +=1
        #             #print "first matche"
        #             if possition >= len(str(dup_list[-1])):
        #                 print "match"
        #         else:
        #             possition = end
        #             #print "no matches found", dup_list



    """

    #print duplicates

    ################trhird logic##############################
    a_tup_num = tuple(nums)
    mid_set_num = set(nums)
    b_set_num = list(mid_set_num)
    a_tup_num = list(a_tup_num)
    b_set_num.sort()
    a_tup_num.sort()
    max_len = len(b_set_num)-1
    pos = 0
    if len(a_tup_num) != len(b_set_num):
        
        while pos <=max_len:
            if a_tup_num[pos] != b_set_num[pos]:
                break
            pos +=1
        return a_tup_num[pos]








    #print int_list


nums = [3798,1, 46565, 6, 7, 886,4,57645879659,34567, 689, 46565, 3424, 444, 4224]
#nums=[1,2,2]
print findDuplicate(nums)
