from hypothesis.utils.conventions import not_set

def accept(f):
    def testResults(self, s=not_set, config=not_set):
        return f(self, s, config)
    return testResults
