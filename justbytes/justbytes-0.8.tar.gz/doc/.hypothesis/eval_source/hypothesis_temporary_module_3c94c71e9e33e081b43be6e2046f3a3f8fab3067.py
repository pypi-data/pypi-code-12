from hypothesis.utils.conventions import not_set

def accept(f):
    def testRepr(self, s=not_set):
        return f(self, s)
    return testRepr
