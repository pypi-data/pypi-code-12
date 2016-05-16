import sys
import pickle
import unittest
import simpletap
import contextlib

try:
    from StringIO import PickleableIO as StringIO
except ImportError:
    # Python 3
    from io import StringIO

from unittest.test.support import LoggingResult


class _Outcome(object):
    def __init__(self, result=None):
        self.expecting_failure = False
        self.result = result
        self.result_supports_subtests = hasattr(result, "addSubTest")
        self.success = True
        self.skipped = []
        self.expectedFailure = None
        self.errors = []

    @contextlib.contextmanager
    def testPartExecutor(self, test_case, isTest=False):
        old_success = self.success
        self.success = True
        try:
            yield
        except KeyboardInterrupt:
            raise
        except:
            exc_info = sys.exc_info()

            if self.expecting_failure:
                self.expectedFailure = exc_info
            else:
                self.success = False
                self.errors.append((test_case, exc_info))
            # explicitly break a reference cycle:
            # exc_info -> frame -> exc_info
            exc_info = None
        else:
            if self.result_supports_subtests and self.success:
                self.errors.append((test_case, None))
        finally:
            self.success = self.success and old_success

    def addError(self, test, exc_info):
        self.errors.append((test, exc_info))


class TestCleanUp(unittest.TestCase):

    def testCleanUp(self):
        class TestableTest(unittest.TestCase):
            def testNothing(self):
                pass

        test = TestableTest('testNothing')
        self.assertEqual(test._cleanups, [])

        cleanups = []

        def cleanup1(*args, **kwargs):
            cleanups.append((1, args, kwargs))

        def cleanup2(*args, **kwargs):
            cleanups.append((2, args, kwargs))

        test.addCleanup(cleanup1, 1, 2, 3, four='hello', five='goodbye')
        test.addCleanup(cleanup2)

        self.assertEqual(test._cleanups,
                         [(cleanup1, (1, 2, 3), dict(four='hello', five='goodbye')),
                          (cleanup2, (), {})])

        self.assertTrue(test.doCleanups())
        self.assertEqual(cleanups,
                         [(2, (), {}),
                          (1, (1, 2, 3), dict(four='hello', five='goodbye'))])

    def testCleanUpWithErrors(self):
        class TestableTest(unittest.TestCase):
            def testNothing(self):
                pass

        test = TestableTest('testNothing')
        outcome = _Outcome()

        # Python 2
        test._resultForDoCleanups = outcome
        # Python 3
        test._outcome = outcome

        exc1 = Exception('foo')
        exc2 = Exception('bar')

        def cleanup1():
            raise exc1

        def cleanup2():
            raise exc2

        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        self.assertFalse(test.doCleanups())

        (test1, (Type1, instance1, _)), (test2, (Type2, instance2, _)) = reversed(outcome.errors)
        self.assertEqual((test1, Type1, instance1), (test, Exception, exc1))
        self.assertEqual((test2, Type2, instance2), (test, Exception, exc2))

    def testCleanupInRun(self):
        blowUp = False
        ordering = []

        class TestableTest(unittest.TestCase):
            def setUp(self):
                ordering.append('setUp')
                if blowUp:
                    raise Exception('foo')

            def testNothing(self):
                ordering.append('test')

            def tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        def cleanup1():
            ordering.append('cleanup1')

        def cleanup2():
            ordering.append('cleanup2')

        test.addCleanup(cleanup1)
        test.addCleanup(cleanup2)

        def success(some_test):
            self.assertEqual(some_test, test)
            ordering.append('success')

        result = unittest.TestResult()
        result.addSuccess = success

        test.run(result)
        self.assertEqual(ordering, ['setUp', 'test', 'tearDown',
                                    'cleanup2', 'cleanup1', 'success'])

        blowUp = True
        ordering = []
        test = TestableTest('testNothing')
        test.addCleanup(cleanup1)
        test.run(result)
        self.assertEqual(ordering, ['setUp', 'cleanup1'])

    def testTestCaseDebugExecutesCleanups(self):
        ordering = []

        class TestableTest(unittest.TestCase):
            def setUp(self):
                ordering.append('setUp')
                self.addCleanup(cleanup1)

            def testNothing(self):
                ordering.append('test')

            def tearDown(self):
                ordering.append('tearDown')

        test = TestableTest('testNothing')

        def cleanup1():
            ordering.append('cleanup1')
            test.addCleanup(cleanup2)

        def cleanup2():
            ordering.append('cleanup2')

        test.debug()
        self.assertEqual(ordering, ['setUp', 'test', 'tearDown',
                                    'cleanup1', 'cleanup2'])


class Test_TextTestRunner(unittest.TestCase):
    """Tests for TextTestRunner."""

    def test_init(self):
        runner = simpletap.TAPTestRunner()
        self.assertFalse(runner.failfast)
        self.assertFalse(runner.buffer)
        self.assertEqual(runner.verbosity, 1)
        self.assertTrue(runner.descriptions)
        self.assertEqual(runner.resultclass, simpletap.TAPTestResult)

    def test_multiple_inheritance(self):
        class AResult(unittest.TestResult):
            def __init__(self, stream, descriptions, verbosity):
                super(AResult, self).__init__(stream, descriptions, verbosity)

        class ATextResult(simpletap.TAPTestResult, AResult):
            pass

        # This used to raise an exception due to TAPTestResult not passing
        # on arguments in its __init__ super call
        ATextResult(None, None, 1)

    def testBufferAndFailfast(self):
        class Test(unittest.TestCase):
            def testFoo(self):
                pass

        result = unittest.TestResult()
        runner = simpletap.TAPTestRunner(stream=StringIO(), failfast=True,
                                         buffer=True)
        # Use our result object
        runner._makeResult = lambda: result
        runner.run(Test('testFoo'))

        self.assertTrue(result.failfast)
        self.assertTrue(result.buffer)

    def testRunnerRegistersResult(self):
        class Test(unittest.TestCase):
            def testFoo(self):
                pass

        originalRegisterResult = simpletap.runner.registerResult

        def cleanup():
            simpletap.runner.registerResult = originalRegisterResult

        self.addCleanup(cleanup)

        result = unittest.TestResult()
        runner = simpletap.TAPTestRunner(stream=StringIO())
        # Use our result object
        runner._makeResult = lambda: result

        self.wasRegistered = 0

        def fakeRegisterResult(thisResult):
            self.wasRegistered += 1
            self.assertEqual(thisResult, result)

        simpletap.runner.registerResult = fakeRegisterResult

        runner.run(unittest.TestSuite())
        self.assertEqual(self.wasRegistered, 1)

    def test_startTestRun_stopTestRun_called(self):
        class LoggingTextResult(LoggingResult):
            separator2 = ''

            def printErrors(self):
                pass

        class LoggingRunner(simpletap.TAPTestRunner):
            def __init__(self, events):
                super(LoggingRunner, self).__init__(StringIO())
                self._events = events

            def _makeResult(self):
                return LoggingTextResult(self._events)

        events = []
        runner = LoggingRunner(events)
        runner.run(unittest.TestSuite())
        expected = ['startTestRun', 'stopTestRun']
        self.assertEqual(events, expected)

    def test_pickle_unpickle(self):
        # Issue #7197: a TextTestRunner should be (un)pickleable. This is
        # required by test_multiprocessing under Windows (in verbose mode).
        stream = StringIO(u"foo")
        runner = simpletap.TAPTestRunner(stream)

        for protocol in range(2, pickle.HIGHEST_PROTOCOL + 1):
            s = pickle.dumps(runner, protocol)
            obj = pickle.loads(s)
            # StringIO objects never compare equal, a cheap test instead.
            self.assertEqual(obj.stream.getvalue(), stream.getvalue())

    def test_resultclass(self):
        def MockResultClass(*args):
            return args

        STREAM = object()
        DESCRIPTIONS = object()
        VERBOSITY = object()
        runner = simpletap.TAPTestRunner(STREAM, DESCRIPTIONS, VERBOSITY,
                                         resultclass=MockResultClass)
        self.assertEqual(runner.resultclass, MockResultClass)

        expectedresult = (runner.stream, DESCRIPTIONS, VERBOSITY)
        self.assertEqual(runner._makeResult(), expectedresult)


if __name__ == "__main__":
    unittest.main()
