from hypothesis.utils.conventions import not_set

def accept(f):
    def testPrecision(self, s=not_set, u=not_set):
        return f(self, s, u)
    return testPrecision
