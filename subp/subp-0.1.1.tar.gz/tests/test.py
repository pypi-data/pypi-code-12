import unittest
import subp
import time


class SimpleTest(unittest.TestCase):

    def test_input(self):
        r = subp.run("sed s/i/I/g", "Hi")
        self.assertEqual(r.std_out.rstrip(), "HI")
        self.assertEqual(r.status_code, 0)

    def test_pipe(self):
        r = subp.run("echo -n 'hi'| tr [:lower:] [:upper:]")
        self.assertEqual(r.std_out, "HI")
        self.assertEqual(r.status_code, 0)

    def test_timeout(self):
        r = subp.run('yes | head', timeout=1)
        self.assertEqual(r.std_out, 'y\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
        self.assertEqual(r.status_code, 0)

    # THIS TEST FAILS BECAUSE expand_args DOESN'T HANDLE QUOTES PROPERLY
    def test_quoted_args(self):
        sentinel = 'quoted_args' * 3
        r = subp.run("python -c 'print \"%s\"'" % sentinel)
        self.assertEqual(r.std_out.rstrip(), sentinel)
        self.assertEqual(r.status_code, 0)

    def test_non_existing_command(self):
        r = subp.run("blah")
        self.assertEqual(r.status_code, 127)


class ConnectedCommandTests(unittest.TestCase):

    def test_status_code_none(self):
        c = subp.connect("sleep 5")
        self.assertEqual(c.status_code, None)

    def test_status_code_success(self):
        c = subp.connect("sleep 1")
        time.sleep(2)
        self.assertEqual(c.status_code, 0)

    def test_status_code_failure(self):
        c = subp.connect("sleeep 1")
        self.assertEqual(c.status_code, 127)

    def test_input(self):
        import pudb; pudb.set_trace()
        test_string = 'asdfQWER'
        r = subp.connect("cat | tr [:lower:] [:upper:]")
        r.send(test_string)
        self.assertEqual(r.std_out, test_string.upper())
        self.assertEqual(r.status_code, 0)

if __name__ == "__main__":
    unittest.main()
