from hypothesis.utils.conventions import not_set

def accept(f):
    def testRfloordivWithSize(self, s1=not_set, s2=not_set):
        return f(self, s1, s2)
    return testRfloordivWithSize
