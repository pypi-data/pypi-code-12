__author__ = 'Shyue Ping Ong'
__copyright__ = 'Copyright 2014, The Materials Virtual Lab'
__version__ = '0.1'
__maintainer__ = 'Shyue Ping Ong'
__email__ = 'ongsp@ucsd.edu'
__date__ = '1/24/14'


import unittest
import warnings

from monty.dev import deprecated, requires


class A:

    @property
    def repl_prop(self):
        pass

    @deprecated(repl_prop)
    @property
    def prop(self):
        pass


class DecoratorTest(unittest.TestCase):

    def test_deprecated(self):

        def func_a():
            pass

        @deprecated(func_a, "hello")
        def func_b():
            pass

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            func_b()
            # Verify some things
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn('hello', str(w[0].message))

    def test_deprecated_property(self):

        class a(object):
            def __init__(self):
                pass

            @property
            def property_a(self):
                pass

            @property
            @deprecated(property_a)
            def property_b(self):
                return 'b'

            @deprecated(property_a)
            def func_a(self):
                return 'a'

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            self.assertEqual(a().property_b, 'b')
            # Verify some things
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            self.assertEqual(a().func_a(), 'a')
            # Verify some things
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))

    def test_deprecated_classmethod(self):

        class a(object):
            def __init__(self):
                pass

            @classmethod
            def classmethod_a(self):
                pass

            @classmethod
            @deprecated(classmethod_a)
            def classmethod_b(self):
                return 'b'

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            self.assertEqual(a().classmethod_b(), 'b')
            # Verify some things
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))

    def test_requires(self):

        try:
            import fictitious_mod
        except ImportError:
            fictitious_mod = None

        @requires(fictitious_mod is not None, "fictitious_mod is not present.")
        def use_fictitious_mod():
            print("success")

        self.assertRaises(RuntimeError, use_fictitious_mod)

        @requires(unittest is not None, "scipy is not present.")
        def use_unittest():
            return "success"

        self.assertEqual(use_unittest(), "success")


if __name__ == "__main__":
    unittest.main()