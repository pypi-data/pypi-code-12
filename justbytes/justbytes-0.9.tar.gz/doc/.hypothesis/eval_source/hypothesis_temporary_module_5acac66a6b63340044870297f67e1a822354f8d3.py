from hypothesis.utils.conventions import not_set

def accept(f):
    def testBounds(self, s=not_set, unit=not_set, rounding=not_set, bounds=not_set):
        return f(self, s, unit, rounding, bounds)
    return testBounds
