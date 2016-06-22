import unittest
from deepthought.utils.DTSettingsConfig import DTSettingsConfig

class DTSettingsTest(unittest.TestCase):
    def testBaseURL(self):
        self.assertEquals("/myfile.php",DTSettingsConfig.baseURL("myfile.php"))

        base_url = "test.org/base/url"
        DTSettingsConfig.sharedSettings({"base_url":base_url})
        self.assertEquals("http://test.org/base/url/myfile.php",DTSettingsConfig.baseURL("myfile.php"))

if __name__ == '__main__':
    unittest.main()
