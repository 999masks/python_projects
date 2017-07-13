def sort_list(nums, k):
    if k<= len(nums):
        nums.sort()
        nums.reverse()

        return nums[k - 1]
    else:
        return "k out of range"


a = [3]

print sort_list(a,1)






