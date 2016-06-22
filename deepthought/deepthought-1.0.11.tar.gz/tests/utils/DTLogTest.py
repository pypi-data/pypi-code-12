import unittest
import tempfile
import re
from deepthought.utils.DTLog import DTLog

class DTLogTest(unittest.TestCase):

    def testError(self):
        DTLog.error_fp = open("/dev/null","w")
        err_msg = DTLog.error("Testing stdout for error log...")
        self.assertTrue(err_msg.find("Testing stdout for error log...") > 0)

    def testDebug(self):
        DTLog.debug_fp = open("/dev/null","w")
        debug_msg = DTLog.error("Testing stdout for debug log...")
        backtrace = DTLog.lastBacktrace()
        self.assertTrue(debug_msg.find("Testing stdout for debug log...") > 0)
        self.assertIsNotNone(backtrace,"Expected backtrace to be returned")

    def testFileWrite(self):
        DTLog.debug_fp = open(tempfile.gettempdir()+"/debug.log","w")
        debug_msg = DTLog.error("Testing file for log...")
        self.assertTrue(debug_msg.find("Testing file for log...") > 0)

    def testInfo(self):
        DTLog.info_fp = open("/dev/null","w")
        info_msg = DTLog.info("Testing stdout for info log...")
        self.assertTrue(info_msg.find("Testing stdout for info log...") > 0)

    def testObjectAsMsg(self):
        obj = {"test":"success"}
        info_msg = DTLog.info(obj)
        self.assertIsNotNone(re.search(r"{\'test\': \'success\'}", info_msg),"Expected json-encoded object")

    def testFormattedMsg(self):
        obj = {"test":"success"}
        info_msg = DTLog.info("The contents of {} look correct",obj)
        self.assertTrue(re.search(r"The contents of .*{\"test\": \"success\"}.* look correct",info_msg),"Expected embedded, json-encoded object")

if __name__ == '__main__':
    unittest.main()
