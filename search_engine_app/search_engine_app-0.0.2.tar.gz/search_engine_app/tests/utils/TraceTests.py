import unittest

from  search_engine_app.utils.Trace import Trace


class TraceTest(unittest.TestCase):

    def test_thread_trace(self):
        try:
            Trace._enable_debug_trace_to_console()
            Trace.thread_trace("Hey ,Console Thread")
            Trace._enable_debug_trace_to_file()
            Trace.thread_trace("Hey ,file Thread")
        except Exception as e:
            self.assertTrue(False,e)
        return

if __name__ == "__main__":
    unittest.main()