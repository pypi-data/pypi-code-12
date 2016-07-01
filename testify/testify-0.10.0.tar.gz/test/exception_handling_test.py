from __future__ import absolute_import
from __future__ import unicode_literals

from re import compile as Regex

import testify as T
from testify import exit


def assert_command(cmd, stdout, stderr, returncode):
    import subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='examples')
    actual_stdout, actual_stderr = proc.communicate()
    actual_stdout = normalize(actual_stdout)
    actual_stderr = normalize(actual_stderr)
    T.assert_equal(stderr, actual_stderr)
    T.assert_equal(stdout, actual_stdout)
    T.assert_equal(returncode, proc.returncode)


def normalize(value):
    value = value.decode('UTF-8')
    for pattern, replacement in (
            (Regex(r' File "[^"]+", line \d+, in '), ' File ..., in '),
            (Regex(r'time [0-9.]+s'), 'time $TIME'),
    ):
        value = pattern.sub(replacement, value)
    return value


class SystemExitTestCase(T.TestCase):
    def test_test(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'systemexit.test'),
            '''
error: systemexit.test Test.test
Traceback (most recent call last):
  File ..., in test
    sys.exit('fake!')
SystemExit: fake!

E
FAILED.  1 test / 1 case: 0 passed, 1 failed.  (Total test time $TIME)
''',

            '',
            exit.TESTS_FAILED,
        )

    def test_setup(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'systemexit.setup'),
            '''
error: systemexit.setup Test.test
Traceback (most recent call last):
  File ..., in __enter__
    return self.gen.next()
  File ..., in wrapper
    fixture()
  File ..., in setUp
    sys.exit('fake!')
SystemExit: fake!

E
FAILED.  1 test / 1 case: 0 passed, 1 failed.  (Total test time $TIME)
''',

            '',
            exit.TESTS_FAILED,
        )

    def test_teardown(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'systemexit.teardown'),
            '''
error: systemexit.teardown Test.test
Traceback (most recent call last):
  File ..., in fixture
    sys.exit('fake!')
SystemExit: fake!

E
FAILED.  1 test / 1 case: 0 passed, 1 failed.  (Total test time $TIME)
''',

            '',
            exit.TESTS_FAILED,
        )

    def test_discovery(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'systemexit.discovery'),
            '''\
DISCOVERY FAILURE!
There was a problem importing one or more tests:

    Traceback (most recent call last):
      File ..., in discover
        mod = __import__(what, fromlist=[str('__trash')])
      File ..., in <module>
        sys.exit('fake!')
    SystemExit: fake!
''',

            '''\
Traceback (most recent call last):
  File ..., in discover
    mod = __import__(what, fromlist=[str('__trash')])
  File ..., in <module>
    sys.exit('fake!')
SystemExit: fake!
''',
            exit.DISCOVERY_FAILED,
        )


class KeyboardInterruptTestCase(T.TestCase):
    def test_test(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'keyboardinterrupt.test'),
            '''\
-
FAILED.  1 test / 1 case: 0 passed, 0 failed.  (Total test time $TIME)
''',

            '',
            exit.TESTS_FAILED,
        )

    def test_setup(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'keyboardinterrupt.setup'),
            '''\
-
FAILED.  1 test / 1 case: 0 passed, 0 failed.  (Total test time $TIME)
''',

            '',
            exit.TESTS_FAILED,
        )

    def test_teardown(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'keyboardinterrupt.teardown'),
            '''\
-
FAILED.  1 test / 1 case: 0 passed, 0 failed.  (Total test time $TIME)
''',

            '',
            exit.TESTS_FAILED,
        )

    def test_discovery(self):
        assert_command(
            ('python', '-m', 'testify.test_program', 'keyboardinterrupt.discovery'),
            '''\
DISCOVERY FAILURE!
There was a problem importing one or more tests:

    Traceback (most recent call last):
      File ..., in discover
        mod = __import__(what, fromlist=[str('__trash')])
      File ..., in <module>
        raise KeyboardInterrupt('fake!')
    KeyboardInterrupt: fake!
''',

            '''\
Traceback (most recent call last):
  File ..., in discover
    mod = __import__(what, fromlist=[str('__trash')])
  File ..., in <module>
    raise KeyboardInterrupt('fake!')
KeyboardInterrupt: fake!
''',
            exit.DISCOVERY_FAILED,
        )
