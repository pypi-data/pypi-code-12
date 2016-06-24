import unittest
from ng_factory import factorize, ArgumentError, NonExistentTypeError, NonExistentModuleError


class FactoryTests(unittest.TestCase):
    """ Here start to define the test and what I need from my library
    """
    def test_raises_arguments(self):
        """testing of assert the exception if receive some missing arguments"""
        self.assertRaises(ArgumentError, factorize)
        self.assertRaises(ArgumentError, factorize, module='factory')
        self.assertRaises(ArgumentError, factorize, object_type='UnknownClass')

    def test_raises_unknown_class(self):
        """Test to raises exception when class don't exist in the module  """
        self.assertRaises(NonExistentTypeError, factorize, module='factory', object_type='UnknownClass')

    def test_raises_unknown_module(self):
        """Test to raises exception when module and class don't exist in the module """
        self.assertRaises(NonExistentModuleError, factorize, module='unknown', object_type='UnknownClass')

    def test_object_creation(self):
        """ Test factorize a class x from module y """
        f = factorize(module='factory', object_type='NonExistentModuleError')
        manual = NonExistentModuleError('factory')
        self.assertEqual(type(f), type(manual))

    def test_type_exception(self):
        """ Test factorize a class x from module y are equal to another instance type """
        f = factorize(module='factory', object_type='NonExistentTypeError')
        manual = NonExistentTypeError('NonExistentTypeError')
        self.assertEqual(type(f), type(manual))

if __name__ == '__main__':
    unittest.main()
