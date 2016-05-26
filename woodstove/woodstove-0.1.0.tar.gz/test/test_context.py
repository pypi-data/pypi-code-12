import unittest
import bottle
from woodstove import context

class TestContext(unittest.TestCase):
    def tearDown(self):
        try:
            del bottle.request.environ['bottle.request.ext.ws_context']
        except KeyError:
            pass

    def test_ctx_push(self):
        c = {'foo': 'bar'}
        context.ctx_push(c)
        self.assertGreater(len(bottle.request.ws_context), 0)
        self.assertIs(context.ctx_get(), c)

    def test_ctx_pop(self):
        c = {'foo': 'bar'}
        context.ctx_push(c)
        self.assertIs(context.ctx_pop(), c)
        self.assertEqual(len(bottle.request.ws_context), 0)

    def test_ctx_get(self):
        c = {'foo': 'bar'}
        context.ctx_push(c)
        t = context.ctx_get()
        self.assertIs(t, c)
        self.assertGreater(len(bottle.request.ws_context), 0)

    def test_ctx_copy(self):
        c = {'foo': 'bar'}
        context.ctx_push(c)
        copy = context.ctx_copy()
        self.assertIsNot(copy[0], c)
        self.assertDictEqual(c, copy[0])

    def test_context_manager(self):
        c = {'foo': 'bar'}

        with context.Context(**c):
            self.assertDictEqual(context.ctx_get(), c)

        self.assertIsNone(context.ctx_get())
