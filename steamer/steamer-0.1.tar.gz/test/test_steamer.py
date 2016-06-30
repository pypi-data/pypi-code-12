import sys
sys.path.append('../steamer')

import unittest
from steamer import steamer as st
from glob import glob
import time
import io
import os

TEST_FILE='test/test.txt'
NEW_FILE='test/test_new.txt'

def overwrite_test_file():
    with open(TEST_FILE,'w') as f:
        f.write("test file")

def remove_file(filename):
    try:
        os.remove(filename)
    except:
        pass

def write_file(filename,content):
    with open(filename,'w') as f:
        f.write(content)

def replace_test_file():
    os.remove(TEST_FILE)
    with open(TEST_FILE,'w') as f:
        f.write("test file")

class TestWatchCommand(unittest.TestCase):
    def setUp(self):
        write_file(TEST_FILE,"test file")
        self.output = io.StringIO()
        # We have to wait a little because the shell has problems keeping up
        # and if we don't wait we'll get some triggers returning empty stdout
        # and stderr
        time.sleep(0.01)

    def tearDown(self):
        remove_file(NEW_FILE)

    def test_empty_setup(self):
        with self.assertRaises(st.CommandException):
            w = st.Watch(None,None,io_out=self.output)

    def test_wrong_files_type(self):
        files = 1
        triggers = 'trigger'
        with self.assertRaises(st.CommandException):
            w = st.Watch(files,triggers,io_out=self.output)

    def test_correct_setup(self):
        expected_files = glob('**/test.txt')
        files = TEST_FILE
        triggers = 't'
        expected_output = "watching files: ['{}']\nusing triggers: ['t']\n".format(TEST_FILE)
        w = st.Watch(files,triggers,io_out=self.output)
        self.assertEqual(w.files,expected_files)
        self.assertEqual(w.triggers,[triggers])
        self.assertEqual(self.output.getvalue(),expected_output)

    def test_run(self):
        expected_files = glob('*.py')
        files = TEST_FILE
        triggers = 'echo hello'
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        overwrite_test_file()
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[0],"watching files: ['{}']".format(TEST_FILE))
        self.assertEqual(lines[1],"using triggers: ['echo hello']")
        self.assertEqual(lines[3],"TRIGGER!: ['echo hello']")
        self.assertEqual(lines[4],"STANDARD OUT:")
        self.assertEqual(lines[5],"hello")

    def test_multiple_globs(self):
        files = [TEST_FILE,'steamer/*.py']
        triggers = 'echo hello'
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        overwrite_test_file()
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[5],"hello")

    def test_multiple_globs_not_all_strings(self):
        files = [TEST_FILE,2]
        triggers = 'echo hello'
        with self.assertRaises(st.CommandException) as cm:
            w = st.Watch(files,triggers,io_out=self.output)
        self.assertEqual(str(cm.exception),
            "files must either be a string or list of strings")

    def test_multiple_triggers(self):
        files = [TEST_FILE,'steamer/*.py']
        triggers = ['echo hello','echo world']
        w = st.Watch(files,triggers,io_out=self.output)
        self.assertEqual(w.triggers,triggers)
        w.run()
        overwrite_test_file()
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[5],"hello")
        self.assertEqual(lines[8],"world")

    def test_multiple_triggers_not_all_strings(self):
        files = [TEST_FILE,'steamer/*.py']
        triggers = ['echo hello',2]
        with self.assertRaises(st.CommandException) as cm:
            w = st.Watch(files,triggers,io_out=self.output)
        self.assertEqual(str(cm.exception),
            "triggers must be a string or list of strings")

    def test_trigger_wrong_type(self):
        files = [TEST_FILE,'steamer/*.py']
        triggers = 2
        with self.assertRaises(st.CommandException) as cm:
            w = st.Watch(files,triggers,io_out=self.output)
        self.assertEqual(str(cm.exception),
            "triggers must be a string or list of strings")

    def test_stdout_and_stderr(self):
        files = [TEST_FILE]
        triggers = 'python test/stdout_and_stderr.py'
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        overwrite_test_file()
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[5],"hello")
        self.assertEqual(lines[8],"world")

    def test_file_removed(self):
        files = [TEST_FILE]
        triggers = ['echo hello']
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[0],"watching files: ['{}']".format(TEST_FILE))
        self.assertEqual(lines[1],"using triggers: ['echo hello']")
        remove_file(TEST_FILE)
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[0],"watching files: ['{}']".format(TEST_FILE))
        self.assertEqual(lines[1],"using triggers: ['echo hello']")
        self.assertEqual(lines[2],"watching files: []")

    def test_file_replaced(self):
        files = [TEST_FILE]
        triggers = ['echo hello']
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[0],"watching files: ['{}']".format(TEST_FILE))
        self.assertEqual(lines[1],"using triggers: ['echo hello']")
        replace_test_file()
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[5],"hello")

    def test_new_file_added(self):
        files = ['test/*.txt']
        triggers = ['echo hello']
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[0],"watching files: ['{}']".format(TEST_FILE))
        self.assertEqual(lines[1],"using triggers: ['echo hello']")
        write_file(NEW_FILE,"new file")
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[0],"watching files: ['{}']".format(TEST_FILE))
        self.assertEqual(lines[1],"using triggers: ['echo hello']")
        self.assertEqual(lines[2],"watching files: ['test/test_new.txt', 'test/test.txt']")

    def test_remove_the_only_file_shouldnt_blow_up(self):
        files = [TEST_FILE]
        triggers = ['echo hello']
        w = st.Watch(files,triggers,io_out=self.output)
        w.run()
        remove_file(TEST_FILE)
        w.run()
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[2],"watching files: []")

    def test_no_files(self):
        files = ['doesntexist']
        triggers = ['echo hello']
        w = st.Watch(files,triggers,io_out=self.output)
        lines = [x.strip() for x in self.output.getvalue().split('\n')]
        self.assertEqual(lines[1],"WARNING: no files are being watched")

class MockCommand:
    def __init__(self):
        self.throw_exception = False
        self.calls = 0

    def run(self):
        self.calls += 1
        if self.throw_exception:
            raise Exception("thrown in run")

class FailingStream (io.StringIO):
    def die(self):
        raise Exception("exception in FailingStream")

    def read(self):
        self.die()

    def readline(self):
        self.die()

class TestThreadedWorker(unittest.TestCase):
    def setUp(self):
        self.mc = MockCommand()

    def test_correct_setup(self):
        tw = st.ThreadedWorker(self.mc, io_in=['a'], io_out=io.StringIO()).run()
        self.assertTrue(self.mc.calls > 0)

    def test_should_halt_on_command_exception(self):
        tw = st.ThreadedWorker(self.mc, io_out=io.StringIO())
        tw.work_thread.start()
        self.assertTrue(tw.work_thread.is_alive())
        self.mc.throw_exception = True
        time.sleep(tw.timeout*2) # must wait for worker thread to notice exception
        self.assertFalse(tw.work_thread.is_alive())

    def test_should_halt_on_run_exception(self):
        tw = st.ThreadedWorker(self.mc, io_in=FailingStream(),
            io_out=io.StringIO())
        tw.work_thread.start()
        self.assertTrue(tw.work_thread.is_alive())
        tw.run()
        self.assertFalse(tw.work_thread.is_alive())

class TestSteamer(unittest.TestCase):
    def test_steamer_ok(self):
        steamer = st.Steamer({'files': [TEST_FILE],
            'triggers': ['echo hello']},
            io_out=io.StringIO())
        self.assertTrue(steamer.worker is not None)
        self.assertEqual(steamer.files,[TEST_FILE])
        self.assertEqual(steamer.triggers,['echo hello'])

if __name__ == '__main__':
    unittest.main()
