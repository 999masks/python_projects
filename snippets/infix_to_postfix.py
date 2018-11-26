from pythonds.basic.stack import Stack
import threading



def infixToPostfix(infixexpr):
    prec = {}
    prec["*"] = 3
    prec["/"] = 3
    prec["+"] = 2
    prec["-"] = 2
    prec["("] = 1
    prec["=="] = 0
    opStack = Stack()
    postfixList = []
    tokenList = infixexpr.split()

    for token in tokenList:
        if token in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or token in "0123456789":
            postfixList.append(token)
        elif token == '(':
            opStack.push(token)
        elif token == ')':
            topToken = opStack.pop()
            while topToken != '(':
                postfixList.append(topToken)
                topToken = opStack.pop()
        else:
            while (not opStack.isEmpty()) and (prec[opStack.peek()] >= prec[token]):
                  postfixList.append(opStack.pop())
            opStack.push(token)

    while not opStack.isEmpty():
        postfixList.append(opStack.pop())
    return " ".join(postfixList)

#print(infixToPostfix("A * B + C * D == 0"))
# print(infixToPostfix("( A + B ) * C - ( D - E ) * ( F + G )"))
#print(infixToPostfix("( A + B ) * ( C + D ) * ( E + F )"))
# print (infixToPostfix("A + B * C * R / ( K + Z )  * E "))



### infix to postfix



"""

(A + B) * (C + D) * (E + F) + > ** +AB + CD + EF
A + B * C * R / K + Z ** E

1. scan word
2. if find lef par, add operators to stack
2.1.create empty list -> fianl_list
2.2 if operator add to
list
2.3 if operand
add
to
stack
3. if righ
par, pop
item
from stack, until

stack is empty
4. if stack is empty and operators
add
to
list
with priority
    5.
    create
    dictianary
    with priority opetarators
operat = dic()
operat["**"] = 0
operat["*"] = 1
operat["/"] = 1
operat["+"] = 2
operat["-"] = 3
5.1 if final
list is empty
add
operator,
if not compare with priority if low insert if high append
"""

class Stack_list:

    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.insert(0, item)

    def pop(self):
        return self.stack.pop()

    def isEmpty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)


def in_to_pref_v1(word):
    l_par = "("
    r_par = ")"
    my_stack = Stack_list()
    final_list = []
    start = False
    operat = dict()
    operat["**"] = 0
    operat["*"] = 1
    operat["/"] = 1
    operat["+"] = 2
    operat["-"] = 3
    letters = "ABCRKZE"
    new_sent = word.split(" ")

    for i in range(len(new_sent)):

        if new_sent[i] in operat.keys():
            if final_list[-1] in operat.keys():
                if operat[final_list[-1]] <= operat[new_sent[i]]:
                    final_list.append(new_sent[i])
                else:
                    # need to swap two operators
                    tmp = final_list.pop()
                    final_list.extend((new_sent[i], tmp))
            else:
                final_list.append(new_sent[i])





        elif new_sent[i] == r_par:

            while not my_stack.isEmpty():
                item = my_stack.pop()
                print "item", item
                final_list.append(item)

        elif start or new_sent[i] in letters:
            my_stack.push(new_sent[i])
        print "stack size", my_stack.size()
    return "".join(final_list)


def in_to_pref(word):
    import string
    l_par = "("
    r_par = ")"
    my_stack = Stack_list()
    final_list = []
    start = False
    operat = dict()
    operat["**"] = 0
    operat["*"] = 1
    operat["/"] = 1
    operat["+"] = 2
    operat["-"] = 3
    letters = string.ascii_uppercase

    new_word = word.split(" ")

    for i in range(len(new_word)):

        item = new_word[i]
        if item in letters:
            my_stack.push(item)

        elif item in operat.keys():
            if len(final_list) == 0:
                final_list.append(item)
            else:
                i = 0
                while i < len(final_list) and final_list[i] in operat.keys():
                    if operat[item] >= operat[final_list[i]]:
                        # final_list.insert(i, item)
                        break
                    else:
                        i += 1
                final_list.insert(i, item)

        elif item == l_par:
            if my_stack.isEmpty():
                continue
            else:
                while not my_stack.isEmpty():
                    final_list.append(my_stack.pop())

        elif item == r_par:
            while not my_stack.isEmpty():
                final_list.append(my_stack.pop())

    return " ".join(final_list)






#wrd = "( A + B ) * C * R / ( K + Z ) ** E"
wrd = "A + B * C * R / ( K + Z )  ** E"

#print in_to_pref(wrd)


def is_poly(sent):
    if len(sent) <= 1:
        return True
    else:
        if len(sent) > 1 and sent[0] == sent[-1]:
            return is_poly(sent[1:-1])
        else:
            return False

print is_poly("kayak")