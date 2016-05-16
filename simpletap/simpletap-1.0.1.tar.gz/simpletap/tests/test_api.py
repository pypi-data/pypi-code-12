import re
import unittest
import simpletap

try:
    from cStringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO


class TestAPI(unittest.TestCase):
    def test_error(self):
        class TestableTest(unittest.TestCase):
            def test_error(self):
                """A test with errors"""

                0 / 0
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_error")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("not ok", "red"))))

        self.assertIn("# ERROR:", text)
        self.assertIn("A test with errors", text)
        self.assertIn("test_error:", text)
        self.assertIn("ZeroDivisionError on file", text)
        self.assertIn("0 / 0", text)

        # No line after the error
        self.assertNotIn("something_extra", text)

        # If no docstring is defined
        self.assertNotIn("test_error (TestableTest)", text)
        self.assertNotIn("# FAIL:", text)
        self.assertNotIn("# EXPECTED_FAILURE:", text)
        self.assertNotIn("# SKIP:", text)

    def test_fail(self):
        class TestableTest(unittest.TestCase):
            def test_fail(self):
                """A failed test"""

                self.assertFalse("This test will fail")
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_fail")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("not ok", "red"))))

        self.assertIn("# FAIL:", text)
        self.assertIn("A failed test", text)
        self.assertIn("test_fail:", text)
        self.assertIn("AssertionError on file", text)
        self.assertIn('self.assertFalse("This test will fail")', text)

        # No line after the error
        self.assertNotIn("something_extra", text)

        # If no docstring is defined
        self.assertNotIn("test_fail (TestableTest)", text)
        self.assertNotIn("# ERROR:", text)
        self.assertNotIn("# EXPECTED_FAILURE:", text)
        self.assertNotIn("# SKIP:", text)

    def test_expected_fail(self):
        class TestableTest(unittest.TestCase):
            @unittest.expectedFailure
            def test_expected_fail(self):
                """Expected fail test"""

                self.assertFalse("This test is expected to fail")
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_expected_fail")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("skip", "yellow"))))

        self.assertIn("# EXPECTED_FAILURE:", text)
        self.assertIn("Expected fail test", text)
        self.assertIn("test_expected_fail:", text)
        self.assertIn("AssertionError on file", text)
        self.assertIn('self.assertFalse("This test is expected to fail")', text)

        # No line after the error
        self.assertNotIn("something_extra", text)

        # If no docstring is defined
        self.assertNotIn("test_expected_fail (TestableTest)", text)
        self.assertNotIn("# ERROR:", text)
        self.assertNotIn("# FAIL:", text)
        self.assertNotIn("# SKIP:", text)

    def test_skip(self):
        class TestableTest(unittest.TestCase):
            @unittest.skipIf(True, "Skipping test for a reason")
            def test_skip(self):
                """This test will be skipped"""

                self.assertTrue("This will not be seen")
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_skip")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("skip", "yellow"))))

        self.assertIn("# SKIP:", text)
        self.assertIn("This test will be skipped", text)
        self.assertIn("Skipping test for a reason", text)

        # If no docstring is defined
        self.assertNotIn("test_skip (TestableTest)", text)

        self.assertNotIn("something_extra", text)
        self.assertNotIn("self.assertTrue", text)
        self.assertNotIn("This will not be seen", text)
        self.assertNotIn("AssertionError on file", text)
        self.assertNotIn("self.assertTrue", text)
        self.assertNotIn("test_skip:", text)
        self.assertNotIn("# ERROR:", text)
        self.assertNotIn("# FAIL:", text)
        self.assertNotIn("# EXPECTED_FAILURE:", text)

    def test_success(self):
        class TestableTest(unittest.TestCase):
            def test_success(self):
                """This will be a success"""

                self.assertTrue("This test will pass")
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_success")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("ok", "green"))))

        self.assertIn("This will be a success", text)

        # If no docstring is defined
        self.assertNotIn("test_success (TestableTest)", text)
        self.assertNotIn("something_extra", text)
        self.assertNotIn("self.assertTrue", text)
        self.assertNotIn("test_success:", text)
        self.assertNotIn("# ERROR:", text)
        self.assertNotIn("# FAIL:", text)
        self.assertNotIn("# EXPECTED_FAILURE:", text)
        self.assertNotIn("# SKIP:", text)

    def test_success_no_docstring(self):
        class TestableTest(unittest.TestCase):
            def test_success_no_doc(self):
                self.assertTrue("This test will pass")
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_success_no_doc")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("ok", "green"))))

        # If no docstring is defined
        self.assertIn("test_success_no_doc (TestableTest)", text)

        self.assertNotIn("This will be a success", text)
        self.assertNotIn("something_extra", text)
        self.assertNotIn("self.assertTrue", text)
        self.assertNotIn("test_success_no_doc:", text)
        self.assertNotIn("# ERROR:", text)
        self.assertNotIn("# FAIL:", text)
        self.assertNotIn("# EXPECTED_FAILURE:", text)
        self.assertNotIn("# SKIP:", text)

    def test_fail_no_docstring(self):
        class TestableTest(unittest.TestCase):
            def test_fail_no_doc(self):
                self.assertFalse("This test will fail")
                lambda: "something_extra"

        result = simpletap.TAPTestResult(StringIO())
        test = TestableTest("test_fail_no_doc")
        test.run(result)

        result.stream.seek(0)
        text = result.stream.read()

        self.assertRegexpMatches(text, "^{} 1 - ".format(
            re.escape(simpletap.result._color("not ok", "red"))))

        self.assertIn("# FAIL:", text)
        # If no docstring is defined
        self.assertIn("test_fail_no_doc (TestableTest)", text)
        self.assertIn("test_fail_no_doc:", text)
        self.assertIn("AssertionError on file", text)
        self.assertIn('self.assertFalse("This test will fail")', text)

        # Docstring from the original fail test
        self.assertNotIn("A failed test", text)

        # No line after the error
        self.assertNotIn("something_extra", text)
        self.assertNotIn("# ERROR:", text)
        self.assertNotIn("# EXPECTED_FAILURE:", text)
        self.assertNotIn("# SKIP:", text)

if __name__ == "__main__":
    from simpletap import TAPTestRunner
    unittest.main(testRunner=TAPTestRunner())

# vim: ai sts=4 et sw=4 ft=python
