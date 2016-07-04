import unittest
from  search_engine_app.services.GoogleSearchService import GoogleSearch
import  os

class googleSearchTests(unittest.TestCase):
    _GOOGLE_RESPONSE_MOKUP_FILE = "googleSearchResponseMockup.html"

    @staticmethod
    def getGoogleResponseMockupFilePath():
        dir = os.path.dirname(__file__)
        path_to_test_mockup_file = os.path.join(dir, googleSearchTests._GOOGLE_RESPONSE_MOKUP_FILE)
        return path_to_test_mockup_file

    def test_search(self):
        try:
            google_search = GoogleSearch()
            response = google_search.search("python")
            responseString  = str(response)
            #path_to_test_settings_file = googleSearchTests.getGoogleResponseMockupFilePath()
            #text_file = open(path_to_test_settings_file, "x")
            #text_file.write(responseString)
            #text_file.close()
            print(responseString)
            self.assertIsNotNone(responseString)
        except Exception as e:
            self.assertTrue(False, e)

if __name__ == "__main__":
    unittest.main()