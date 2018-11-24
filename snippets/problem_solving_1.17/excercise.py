

class Fraction():
    def __init__(self, Num, Den):
        self.GCD(Num, Den)
        self.Num = self.GCD(Num, Den)[0]
        self.Den = self.GCD(Num, Den)[1]

    def GCD(self, Num, Den):
        assert Den != 0, "Denominator cannot be a zero: %d"%Den
        new_d = Den
        new_n = Num
        while Den:
            Num, Den = Den, Num % Den
        Den = new_d / Num
        Num = new_n / Num
        return Num, Den

    def getNum(self):
        return int(self.Num)

    def getDen(self):
        return int(self.Den)

    def CommonDenom(self, Fraction):
        commondenom = Fraction.getDen() * self.Den
        return commondenom

    def __sub__(self, Fraction):
        sub_eq_Num = (Fraction.getDen()* self.Num)  - (self.Den* Fraction.getNum())
        return self.GCD(sub_eq_Num, self.CommonDenom(Fraction))


    def __mul__(self, Fraction):
        multipl_Num = Fraction.getNum() * self.Num
        multipl_Den = Fraction.getDen() * self.Den
        return  self.GCD(multipl_Num, multipl_Den)

    def __truediv__(self, other):
        division_num





a = Fraction(0, 2)
b = Fraction(0, 0)
#print a.__sub__(b)
print a.__mul__(b)


# def simplify(n, d):
#     new_d = d
#     new_n = n
#     while d:
#         n,d = d,n%d
#     d = new_d/n
#     n = new_n/n
#     return  "numerator: %d, denumerator %d"%(n,d)
#





