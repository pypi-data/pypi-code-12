import unittest
from deepthought.utils.DTSettings import DTSettings

class DTSettingsTest(unittest.TestCase):
    def testNewSettings(self):
        DTSettings.sharedSettings({"test":True})
        settings = DTSettings.sharedSettings()
        self.assertTrue(settings["test"])

    def testSharedReference(self):
        settings = DTSettings.sharedSettings()
        settings["test"] = True
        settings = DTSettings.sharedSettings()
        self.assertTrue(settings["test"])

if __name__ == '__main__':
    unittest.main()
