import unittest
import tempfile
from deepthought.utils.DTSettingsStorage import DTSettingsStorage

class DTSettingsTest(unittest.TestCase):
    def setUp(self):
        #settings = DTSettingsStorage.sharedSettings()
        #settings = {} # clear out any old shared settings
        DTSettingsStorage.sharedSettings({
            "test":{
                "connector":"DTSQLiteDatabase",
                "dsn":"file://"+tempfile.gettempdir()+"/test_db.sqlite"
            },"other":{
                "connector":"DTSQLiteDatabase",
                "dsn":"file://"+tempfile.gettempdir()+"/other_db.sqlite"
            }
        })

    def testConnect(self):
        self.assertIsNotNone(DTSettingsStorage.connect("test"))
        self.assertIsNotNone(DTSettingsStorage.connect("other"))

    def testDefaultStore(self):
        test = DTSettingsStorage.connect("test")
        self.assertEquals(test,DTSettingsStorage.defaultStore(),"Expected default store to be 'test'.")

if __name__ == '__main__':
    unittest.main()
