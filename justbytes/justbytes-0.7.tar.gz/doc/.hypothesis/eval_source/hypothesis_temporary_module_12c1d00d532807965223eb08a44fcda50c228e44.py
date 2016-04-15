from hypothesis.utils.conventions import not_set

def accept(f):
    def testNeg(self, s=not_set):
        return f(self, s)
    return testNeg
