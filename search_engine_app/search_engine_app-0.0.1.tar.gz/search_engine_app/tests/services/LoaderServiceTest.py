import unittest

from search_engine_app.services.LoaderService import LoaderService
from  search_engine_app.tests.services.googleSearchTests import googleSearchTests

mockupPath = googleSearchTests.getGoogleResponseMockupFilePath()
LoaderService.setMockupMode(mockupPath)

class LoaderServiceTest(unittest.TestCase):

    def test_retrieveContentFromListOfQueries(self):
        try:
            query = ["https://docs.python.org","some search"]
            (good_reponse,wrong_responses,wrong_queries) = LoaderService.retrieveContentFromListOfQueries(query)
            print(good_reponse)
            if isinstance(good_reponse, Exception):
                self.assertTrue(False, "This must be response from url")
        except Exception as e:
            self.assertTrue(False, e)


    def test_retrieveContentFromQuery(self):
        try:

            query = "https://docs.python.org"
            actual = LoaderService._retrieveContent(query)
            print(actual)
            if isinstance(actual,Exception):
                self.assertTrue(False,"This must be response from url")
        except Exception as e:
            self.assertTrue(False,e)



if __name__ == "__main__":
    unittest.main()