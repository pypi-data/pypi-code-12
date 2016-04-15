from hypothesis.utils.conventions import not_set

def accept(f):
    def testRoundingToBytes(self, n=not_set):
        return f(self, n)
    return testRoundingToBytes
