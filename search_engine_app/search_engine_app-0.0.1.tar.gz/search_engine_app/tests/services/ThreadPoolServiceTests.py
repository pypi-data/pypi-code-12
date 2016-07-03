import time
import unittest

from search_engine_app.services.ThreadPoolService import ThreadPoolService


class ThreadPoolServiceTest(unittest.TestCase):

    @staticmethod
    def _wait_with_return(x):
        time.sleep(1)
        return x

    def test_processTasksWithArgumentsTest(self):
        try:
            pool_size = 4
            arguments_array = ["1",2,"c","d","e"]
            actual = ThreadPoolService.processTasksWithArguments(pool_size, arguments_array, ThreadPoolServiceTest._wait_with_return)
            expected = arguments_array
            self.assertEquals(actual,expected,'The data was not processed correctly')
        except Exception as e:
            self.assertTrue(False,e)
        return

if __name__ == "__main__":
    unittest.main()