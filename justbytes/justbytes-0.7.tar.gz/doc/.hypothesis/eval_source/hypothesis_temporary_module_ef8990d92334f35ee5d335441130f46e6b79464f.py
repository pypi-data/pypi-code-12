from hypothesis.utils.conventions import not_set

def accept(f):
    def testDistributivity1(self, s=not_set, n=not_set, m=not_set):
        return f(self, s, n, m)
    return testDistributivity1
