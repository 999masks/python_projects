import turtle

def tree(branchLen,t):
    print branchLen
    if branchLen > 5:
        t.forward(branchLen)
        t.right(20)
        tree(branchLen-20,t)
        t.left(40)
        tree(branchLen-20,t)
        t.right(20)
        t.backward(branchLen)

def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    t.left(90)
    t.up()
    t.backward(100)
    t.down()
    t.color("green")
    tree(50,t)
    myWin.exitonclick()

#main()

def computeFactorial(number):
    if number == 1:
        return number
    else:
        return computeFactorial(number -1) * number

print computeFactorial(4)

