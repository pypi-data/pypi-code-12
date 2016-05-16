from hypothesis.utils.conventions import not_set

def accept(f):
    def testExactness(self, p=not_set, q=not_set, n=not_set, m=not_set):
        return f(self, p, q, n, m)
    return testExactness
