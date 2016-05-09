from hypothesis.utils.conventions import not_set

def accept(f):
    def testSettingInputConfig(self, config=not_set):
        return f(self, config)
    return testSettingInputConfig
