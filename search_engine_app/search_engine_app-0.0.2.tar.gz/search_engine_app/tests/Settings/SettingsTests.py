import os
import unittest

from search_engine_app.Settings.Settings import Settings


class SettingsTests(unittest.TestCase):
    SETTINGS_FILE_NAME = 'settings_tests.ini'
    def test_processTasksWithArgumentsTest(self):
        try:
            dir = os.path.dirname(__file__)
            path_to_test_settings_file = os.path.join(dir, self.SETTINGS_FILE_NAME)
            Settings.setPathToFile(path_to_test_settings_file)
            missing_data = Settings._get('missing_data')
            self.assertIsNone(missing_data)
            actual_data1 = Settings._get('data')
            self.assertEquals(actual_data1,"123")
            actual_data2 = Settings._get('google_data')
            self.assertEquals(actual_data2,"123456")

            traceMode = Settings.getTraceMode()
            self.assertEquals(traceMode, 'file')

            poolCapacity = Settings.getThreadPoolCapacity()
            self.assertEquals(poolCapacity, "6")

            traceFile = Settings.getTraceFile()
            self.assertEquals(traceFile, 'path_to_file')
        except Exception as e:
            self.assertTrue(False,e)
        return

if __name__ == "__main__":
    unittest.main()