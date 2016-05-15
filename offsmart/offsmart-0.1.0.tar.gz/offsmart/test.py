import unittest
import offsmart
import time
from collections import deque
import random


class Test(unittest.TestCase):

    def reliable_test(self):

        rd = deque([])
        def send_data(data):
            if offsmart.Offline.active_internet_connection():
                self.assertEqual(data, str(rd.popleft()))
                return True
            else:
                return False

        off = offsmart.Offline('data.db', send_data, delay=1)

        for i in range(0,13):
            number = random.random()
            rd.append(number)
            off.send(str(number))

        time.sleep(30)


if __name__ == '__main__':
    unittest.main()
