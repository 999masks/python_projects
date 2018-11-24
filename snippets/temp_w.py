"""
def solution_old(T):
    # write your code in Python 3.6
    candy_inventory = dict()
    variaty = 0
    for i in T:
        if not i in candy_inventory.keys():
            candy_inventory[i] = 1
            variaty +=1
        else:
            candy_inventory[i] = candy_inventory[i] + 1


    return variaty


g = [3, 4, 7, 7, 6, 80, 80, 10000000, 50, 6]



def solution(T):
    #print (len(T))
    unique_candies = set(T)

    if len(unique_candies) >= len(T)/2:
        return len(T)/2
    else:
        return len(unique_candies)



print solution(g)
"""

nm = [1,2,3,4,5,6,7,8,9,10]

def prefix_average(S):
	n=len(S)
	A=[0]* n
	for j in range(n):
		total = 0
		for i in range(j+1):
			total += S[i]
		A[j] = total/(j+1)
	return A

#print prefix_average(nm)
# return [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

nm = [1,1,2,3,4,5,6,7,8,9,10]

def aver(list_data):
	avg_data = []
	for i in range(len(list_data)):
		tmp = 0
		for item in range(1, i+1):
			tmp_list = list_data[:item+1]
			tmp = sum(tmp_list)//len(tmp_list)
		avg_data.append(tmp)
	return avg_data

# print (aver(nm))

def prefix_agerage_2(S):
	n = len(S)
	A = [0] * n
	for j in range(n):
		A[j] = sum(S[0:j+1]) / (j + 1)
		#A[j] = sum(S[0:j + 1]) / (j + 1)
	return A
# return [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
#print prefix_agerage_2(nm)

def prefix_average_3(S):
	n = len(S)
	A = [0] * n
	total = 0
	for i in range(n):
		total += S[i]
		A[i] = total/(i+1)
	return A

# print prefix_average_3(nm)

def find_joints(A, B, C):
	for a in A:
		for b in B:
			if a == b:
				for c in C:
					if b==c:
						return True
	return False

A = range(2,70)
B = range(69,90)
C = range(68, 170)
# print find_joints(A, B, C)

def find_dupl(data_list):
	tmp = range(len(data_list))
	for i in tmp:
		if data_list[i-1] == data_list[i]:
			return True

#print find_dupl(nm)


nm = [-1,-2,-3,-4,-5]
 # target -8

# cases
# short list
# repeated list
# sum = 0
# negative numbers

def add_to(list_data, target_sum):
	tmp_lst = range(len(list_data))
	for i in tmp_lst:
		ind_1 = i
		for b in tmp_lst[ind_1+1:]:
			if list_data[b] + list_data[i] == target_sum:
				ind_2 = b
				return ind_1, ind_2


# print add_to(nm, -8)
'''
a = "2 -> 4 -> 3"
b = "5 -> 6 -> 4"
a = a.split("->")
b = b.split("->")
a = a[::-1]
b = b.reverse()

final_list = []

def sum_link_lins_elements(a, b):
	a = "2 -> 4 -> 3"
	b = "5 -> 6 -> 4"
	a = a.split("->")
	b = b.split("->")
	a = a[::-1]
	b.reverse()
	print a, b
	lst = list(reversed(range(len(a))))
	new_list = []
	
	for i in lst:
		try:
			tmp_sum = (int(a[i]) + int(b[i]))
			if tmp_sum > 9:

		except:
			pass
		print final_list

sum_link_lins_elements(a,b)

import time
def draf_eng_ruiler(lenght):

	if lenght == 0:
		print ("----0")
		return "done"
	else:
		time.sleep(0.2)
		cr = lenght % 8
		if cr == 0:
			print ("---- {}").format(lenght // 8)
		elif lenght % 6 == 0:
			print ("--")
		elif lenght % 4 == 0:
			print ("---")
		elif lenght % 2 == 0:
			print ("--")
		else:
			print ("-")
		draf_eng_ruiler(lenght -1)



draf_eng_ruiler(32)
'''

def bad_fibonaci(n):
	if n <=1:
		return n
	else:
		return bad_fibonaci(n-1) + bad_fibonaci(n-2)


# print bad_fibonaci(50)

def good_fib(n):
	if n <= 1:
		return (n, 0)
	else:
		a,b = (good_fib(n-1))
		return (a+b, a)



def bin_search_old(lst, trg):
	# mid = len(lst // 2)

	if False:
		return False
	else:
		low = lst[0]
		high = lst(len(lst - 1))
		mid = (low + high) //2
		if trg == lst[mid]:
			return mid
		elif trg < lst[mid]:
			high = mid - 1
			return bin_search(lst, trg)
		else:
			low = mid +1
			return bin_search(lst, trg)

import time

def bin_search_works(lst, trg):
	md_ind = len(lst) // 2
	if lst[md_ind] == trg:
		return trg
	elif trg > lst[md_ind]:
		lst = lst[md_ind:]
		return bin_search(lst, trg)
	else:
		lst = lst[:md_ind]
		return bin_search(lst, trg)

def bin_search(lst, trg):

	mid = len(lst) // 2
	if  lst[mid] == trg:
		return mid
	elif trg > mid:
		lst = lst[mid:]
		return bin_search(lst, trg)
	else:
		lst = lst[:mid]
		return bin_search(lst, trg )


#print bin_search(range(70000000), 8)

def bin_sum(lst, start, stop):
	if start >= stop:
		return 0
	if start == stop - 1:
		return lst[start]
	else:
		mid_ind = (stop + start) // 2
		return bin_sum(lst, start, mid_ind) + bin_sum(lst, mid_ind, stop)

# print bin_sum(range(1003), 0, 1003)



class LinkedStack:
	class _Node:
		__slots__ = "_elements", "_next"

		def __init__(self, element, next):
			self._element = element
			self._next = next

	def __init__(self):
		self._head = None
		self._size = 0

	def __len__(self):
		return self._size

	def is_empty(self):
		return self._size == 0

	def push(self, e):
		self_head = self._Node(e, self._head)
		self._size += 1

	def top(self):
		if self.is_empty():
			raise Empty("Stack is empty")
		return self._head._element

	def pop(self):

		if self.is_empty():
			raise Empty("Stack is empty")
		answer = self._head._element
		self._head = self._head._enxt
		self._size -= 1
		return	answer

#
# my = LinkedStack()
# print my.is_empty()
# my.top()
# my.push("da")
# print my.is_empty()
# my.push("fs")
# my.push("df")
# print my.top()

class sum_num:
	def __init__(self, l1, l2):
		self.l1 = l1
		self.l2 = l2

	def reverse(self, lst):
		return lst[::-1]

	def gen_num(self, lst):
		num = 0
		_max = len(lst)-1
		print _max
		for i in lst:
			num = num + i * 10 ** _max
			_max -= 1
		return num

	def summing(self, num1, num2):
		return num1 + num2

	def make_list(self, num):
		new_lst = []
		for i in str(num):
			new_lst.append(i)
		return new_lst[::-1]

	def addup(self):
		nm1 = self.reverse(self.l1)
		nm2 = self.reverse(self.l2)
		total = self.summing(self.gen_num(nm1), self.gen_num(nm2))
		return self.make_list(total)

# l1 = (3,4,5)
# l2 = (5,6,1)
l1 =[2,4,3]
l2 = [5,6,4]

# a = sum_num(l1, l2)
# # print a.reverse(l1)
# print a.gen_num(l1)
# print "adf", a.addup()

import time


# data = {"a":0, "b" : 1}
data = dict()
def longest_sub_leng(s):
	global data
	if len(data) > len(s):
		return len(data)
	else:
		tmp_lst = range(len(s))
		for i in tmp_lst:
			if s[i] not in data.keys():
				data[(s[i])] = i
			else:
				data = {}
				data[(s[i])] = i
			return longest_sub(s[1:])
"""
1. loop trough cstring
2. record charachte and possition if not in dict
3. if repeeat reset dic and recrd current char
4. 
"""


def longest_sub(s):
	data = []
	new_data = []

	for i in range(len(s)):
		if s[i] not in data:
			data.append(s[i])
			print "top data", data

		else:
			if len(new_data) < len(data):
				new_data = data
			slice_loc = data.index(s[i])
			print "slice", slice_loc
			data = data[slice_loc + 1:]
			data.append(s[i])


	if len(new_data) < len(data):
		return len(data)
	else:
		return len(new_data)

st = "abcabcbb" # 3
#st = "jbpnbwwd" #4
# print longest_sub(st)
#############################################
def find_median(nums1, nums2):
	array_total = nums1 + nums2
	array_total.sort()
	med_ind = len(array_total) // 2
	if len(array_total) % 2 == 0:
		return (array_total[med_ind - 1] + array_total[med_ind]) / 2.0
	else:
		return array_total[med_ind]
ar1 =[1,2]
ar2 = [3]
# print "median", find_median(ar1, ar2)
##############################
def find_max_polyndrome(s):
	max_str = ""
	n = 1
	if 0 < len(s) < 2:
		return s
	while n < len(s):
		for i in range(len(s)-n):
			if s[i] == s[i+n]:
				if n < 3:
					max_str = s[i:(i + n + 1)]

				elif n >= 3: # from here we need to check inner chars
					n_1 = 1
					while n_1 < (n+1)/2 and s[i+n_1] == s[i+n-n_1]:
						n_1 +=1
						if n_1+1 == (n+1)/2: # all nested char tested
							if len(max_str) < len(s[i:i+n+1]):
								max_str = s[i:i+n+1]

			else:
				pass

		n +=1

	return max_str
s = "aba"
#s = "bc"
#s = "babad"
#s = "babad"
# print find_max_polyndrome(s)

##############################
class linked_list:
	# ---------------Nested node class
	class _Node:
		__slots__ = "_element", "_next"

		def __init__(self, element, next):
			self._element = element
			self._next = next

	# -------stack nethods

	def __init__(self):
		self._head = None
		self._size = 0

	def __len__(self):
		return self._size

	def is_empty(self):
		return self._size == 0

	# will generate new node
	def push(self, new_node):
		self._head = self._Node(new_node, self._head)
		self._size += 1

	def top(self):
		if self.is_empty():
			raise ValueError("Stack is empty")
		return self._head._element

	def pop(self):
		if self.is_empty():
			raise ValueError("Stack is empty")
		answer = self._head._element
		self._head = self._head._next
		self._size -= 1
		return answer
########### LED CODE #######
# 1. create linked list object
# 2. add numbers to it
#
#

# l1 = linked_list()
# l2 = linked_list()
# # create l1 LL
# lst_1 = (3,4,5)
# lst_2 = (6,7,8)
#
# for i in range(len(lst_1)):
# 	l1.push(lst_1[i])
# 	l2.push(lst_2[i])
#
# l1_list = []
# l2_list = []
# while not l1.is_empty():
#
# 	l1_list.append((l1.pop()))


l1_data = (2, 4, 3)
l2_data = (5, 6, 4)

l1 = linked_list()
l2 = linked_list()
l3 = linked_list()

for i in range(len(l1_data)):
	l1.push(l1_data[i])
	l2.push(l2_data[i])

l1_int = 0
l2_int = 0
expon = 0
# print l1.is_empty()

while not l1.is_empty():
	l1_int = l1_int + (l1.pop()) * (10 ** expon)
	l2_int = l2_int + (l2.pop()) * (10 ** expon)
	expon += 1
	sum = l1_int + l2_int
	new_sum_str = str(sum)

for i in new_sum_str:
	l3.push(i)



#############test##############

# while not l3.is_empty():
# 	print "poping", l3.pop()
s1 = range(20)
s2 = range(4,44, 2)
# print "s1", (s1)
# print "s2", (s2)
S = []
def mege_Sort_not_complete(s1, s2, S):
	print "Merge sort"
	print "################ notmcomplete"
	i=j=0
	if len(s1) != len(s2):
		raise ValueError("not same lengh")
	while i or j < len(s1):
		time.sleep(1)
		if s1[i] >= s2[j]:
			S.append(s2[j])
			j += 1
			if s1[i] <= s2[j] < len(s1):
				S.append(s1[i])
				i += 1
			else:
				S.append(s2[j])
				j += 1
			# print "S", S, "i", i, "j", j
		else:
			S.append(s1[i])
			i += 1
			if s2[j] < s1[i] < len(s2):
				S.append(s2[j])
				j += 1
			else:
				S.append(s1[i])
				i += 1
		print "S", S, "i", i, "j"
	if i == len(s2) or (j < len(s1) and s1[j] < s2[i]):
		pass

# 		S[j] = s1[j]
# 		j +=1
# 	else:
# 		S[i] = s2[i]
# 		i +=1
#
#
#
#
# print mege_Sort(s1, s2, S)

def in_place_q_serach(S, a, b):
	if a >= b:
		return S
	left = a
	right = b-1
	pivot = S[b]
	while left <= right:
		while left <= right and S[left] < pivot:
			left += 1
		while left <= right and pivot < S[right]:
			right -= 1
		if left <= right:
			S[left], S[right] = S[right], S[left]
			left, right = left + 1, right - 1

	S[left], S[b] = S[b], S[left]

	in_place_q_serach(S, a, left - 1)
	in_place_q_serach(S, left + 1, b)

r = [3,4,2,5,3,1,3,2,1,6,8]
#print "in place", in_place_q_serach(r, 0, 10)

def an_finder(s1, s2):
	match = 0
	if len(s1) != len(s2):
		return "Not match lenght"

	for i in range(len(s1)):

		for b in s2:
			if s1[i] == b:
				match += 1
	if match == len(s1):
		return "got match"




def anagramSolution1(s1,s2):
    alist = list(s2)

    pos1 = 0
    stillOK = True

    while pos1 < len(s1) and stillOK:
        pos2 = 0
        found = False
        while pos2 < len(alist) and not found:
            if s1[pos1] == alist[pos2]:
                found = True
            else:
                pos2 = pos2 + 1

        if found:
            alist[pos2] = None
        else:
            stillOK = False

        pos1 = pos1 + 1

    return stillOK




s1 = "abcde"
s2 = "cb   "
# s1 = 'abcd'
# s2	= 'dcba'
# print an_finder(s1,s2)
# print(anagramSolution1(s1,s2))
###########################################

import timeit

################## Stack

from pythonds.basic.stack import Stack

def revstring(mystr):
    S= Stack()
    r_rev = ""
    for i in mystr:
        S.push(i)
    while not S.isEmpty():
       r_rev = r_rev + S.pop()
    return r_rev

#print revstring('apple')
# testEqual(revstring('x'),'x')
# testEqual(revstring('1234567890'),'0987654321')

def parChecker(symbol):

	s = Stack()
	first_occur = False
	for i in symbol:
		if i == "(":
			s.push(i)
		elif i == ")":
			if s.isEmpty():
				return "Not balanced"
			else:
				s.pop()

	if s.isEmpty():
		return  "balanced"
	else:
		return  "Not balanced"

# print ( parChecker('(((dfaas())))') )
# print(parChecker('(()'))

def univ_to_bin_conv(number, base):
	# import Stack mod
	s = Stack()
	bin_dic = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZZ"
	bin = ""
	while number > 0:
		s.push(number % base ) # this more idiomatic :)
		number = number // base
	while not s.isEmpty():
		bin = bin + bin_dic[s.pop()]
	return bin

# print univ_to_bin_conv(26, 26)


class my_linked_list:
	class _Node:
		__slot__ = "_element", "_next"

		def __init__(self, element, next):
			self._element = element  # data holder
			self._next = next  # will be referiong next head

	def __init__(self):
		self._head = None
		self._size = 0

	def _is_empty(self):
		return self._size == 0

	def pop(self):
		if self._is_empty:
			raise Error("Empty list")
		answer = self._head._element
		self._head = self._head._next
		self._size -= 1
		return answer

	def push(self, new_node):
		self._head = self._Node(new_node, self._head)
		self._size += 1

	def _len(self):
		return self._size

	def top(self):
		return self._head_element

my = my_linked_list()
my.push("a")
my.push("b")