from hypothesis.utils.conventions import not_set

def accept(f):
    def testDistributivity2(self, p=not_set, q=not_set, n=not_set):
        return f(self, p, q, n)
    return testDistributivity2
