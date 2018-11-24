import time
def bin_to_dec(bin_num):
    dec = 0 # decomal accululator
    rev = list(bin_num) # change string to list, for use pop function
    pos = 0 # position iterable, to keep index
    while len(rev) > 0: # keep doing until last item got poped
        dec = dec + int(rev.pop()) *(2**pos)
        pos  +=1
    return dec

#print bin_to_dec("101011")


def dec_to_bin(dec_num):
    bin_ = "" # string accumulator
    while dec_num !=0:  # keep dividing until it reaches to 0
        temp_bin = dec_num%2 # remaining is part of the bin number
        bin_ = bin_ + str((temp_bin))
        dec_num = (dec_num-temp_bin)/2
        pre_bin = bin_[::-1] # rebese the string

    return (int(pre_bin, base=10)) # change to binary likke representation

#print dec_to_bin(280)

def bin_to_hex(bin_num):
    """
    bi_num 01001
    hex_num 9
    :param bin_num:
    :return:
    """
    hex_digs = "0123456789ABCDEF"
    pre_hex = []
    i = len(line)
    while i > 0:
        time.sleep(1)
        if i >4:
            temp = (line[(i-4):i])
            pre_hex.append()
            i = i-4
        else:
            pre_hex.append(line[:i])
            break




line = "1234567890"
import time



#print [line[i-4:i] for  i in range(0,len(line), 4)]

class Stack_list:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.insert(0, item)

    def pop(self):
        return self.stack.pop()



def integer_to_bin(nmb):
    rem_list = Stack_list()
    while nmb != 0:
        remainder = nmb % 2
        rem_list.push(remainder)
        nmb = (nmb - remainder) / 2
    #rem_list.push(nmb / 2)
    return rem_list

a =  integer_to_bin(46)
for i in range(10):
	print a.pop()


# print integer_to_bin(17).pop()
# print integer_to_bin(17).pop()
# print integer_to_bin(17).pop()