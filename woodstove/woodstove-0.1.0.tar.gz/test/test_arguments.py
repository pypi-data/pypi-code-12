import unittest
from woodstove import arguments, exceptions

class TestArgument(unittest.TestCase):
    def test_argument_correct_type(self):
        args = {'foo': 1}
        a = arguments.Argument('foo', (int,))
        self.assertDictEqual(a.check(args), args)

    def test_argument_incorrect_type(self):
        a = arguments.Argument('foo', (int,))
        with self.assertRaises(exceptions.ArgumentException):
            a.check({'foo': 'bar'})

    def test_argument_default(self):
        a = arguments.Argument('foo', (int,), default=1)
        self.assertDictEqual({'foo': 1}, a.check({}))

    def test_argument_optional(self):
        a = arguments.Argument('foo', (int,), optional=True)
        self.assertDictEqual({}, a.check({}))

    def test_hook_called(self):
        private = {'count': 0}

        def callback(arg, val, func, opts):
            opts['private']['count'] += 1

        a = arguments.Argument('foo', (int,))
        a.hook(callback, private)
        a.check({'foo': 1})
        self.assertEqual(private['count'], 1)

class TestStringArgument(unittest.TestCase):
    def test_string(self):
        args = {'foo': 'bar'}
        a = arguments.String('foo')
        self.assertDictEqual(args, a.check(args))

class TestIntegerArgument(unittest.TestCase):
    def test_integer(self):
        args = {'foo': 1}
        a = arguments.Integer('foo')
        self.assertDictEqual(args, a.check(args))

class TestFloatArgument(unittest.TestCase):
    def test_float(self):
        args = {'foo': 1.5}
        a = arguments.Float('foo')
        self.assertDictEqual(args, a.check(args))

class TestNumberArgument(unittest.TestCase):
    def test_float(self):
        args1 = {'foo': 1}
        args2 = {'foo': 1.5}
        a = arguments.Number('foo')
        self.assertDictEqual(args1, a.check(args1))
        self.assertDictEqual(args2, a.check(args2))

class TestBoolArgument(unittest.TestCase):
    def test_bool(self):
        args = {'foo': False}
        a = arguments.Bool('foo')
        self.assertDictEqual(args, a.check(args))
