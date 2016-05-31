
class Int(int):

    def roman(self):
        num = self
        roman=''
        table=[['M',1000], ['CM',900], ['D',500], ['CD',400],
                ['C',100], ['XC',90], ['L',50], ['XL',40],
                ['X',10], ['IX',9], ['V',5], ['IV',4], ['I',1]]
        for pair in table:
            while num - pair[1] >= 0:
                num -= pair[1]
                roman += pair[0]
        return roman
