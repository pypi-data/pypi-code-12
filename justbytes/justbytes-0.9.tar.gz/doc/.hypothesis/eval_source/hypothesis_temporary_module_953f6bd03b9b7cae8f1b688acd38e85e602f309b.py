from hypothesis.utils.conventions import not_set

def accept(f):
    def testRounding(self, i=not_set):
        return f(self, i)
    return testRounding
