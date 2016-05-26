import unittest
from woodstove import hooks

class TestHooks(unittest.TestCase):
    def tearDown(self):
        hooks.__hooks__ = {}

    def test_get_hook_table(self):
        self.assertDictEqual(hooks.get_hook_table('foo'), {})
        hooks.register_hook('bar', 'baz', 'zuz')
        self.assertDictEqual(hooks.get_hook_table('bar'), {'baz': ['zuz']})

    def test_register_hook(self):
        ''' '''
        hooks.register_hook('bar', 'baz', 'zuz')
        self.assertDictEqual(hooks.get_hook_table('bar'), {'baz': ['zuz']})

    def test_remote_hook(self):
        hooks.register_hook('bar', 'baz', 'zuz')
        hooks.remove_hook('bar', 'baz', 'zuz')
        self.assertDictEqual(hooks.get_hook_table('bar'), {'baz': []})

    def test_hook_decorator(self):
        @hooks.hook('foo', 'bar')
        def test(): pass
        t = hooks.get_hook_table('foo')
        self.assertDictEqual(t, {'bar': [test]})

    def test_call_hooks(self):
        called = {'count': 0, 'arg': None}
        @hooks.hook('foo', 'bar')
        def test(a):
            called['count'] += 1
            called['arg'] = a
        hooks.call_hooks('foo', 'bar', 'zuz')
        self.assertEqual(called['count'], 1)
        self.assertEqual(called['arg'], 'zuz')
