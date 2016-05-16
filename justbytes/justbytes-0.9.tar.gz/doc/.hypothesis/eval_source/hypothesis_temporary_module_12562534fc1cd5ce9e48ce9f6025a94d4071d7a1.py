from hypothesis.utils.conventions import not_set

def accept(f):
    def testMultiplication(self, s=not_set, n=not_set):
        return f(self, s, n)
    return testMultiplication
