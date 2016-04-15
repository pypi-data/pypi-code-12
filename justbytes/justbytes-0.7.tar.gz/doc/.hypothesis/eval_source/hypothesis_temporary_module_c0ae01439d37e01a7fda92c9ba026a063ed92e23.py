from hypothesis.utils.conventions import not_set

def accept(f):
    def testAssociativity(self, p=not_set, q=not_set, r=not_set):
        return f(self, p, q, r)
    return testAssociativity
