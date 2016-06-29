import time

from django.test import TestCase
from tornado.concurrent import Future
from tornado.escape import json_decode
from tornado.testing import gen_test
from tornado.web import Application

from tornado_websockets.modules.progress_bar import ProgressBar
from tornado_websockets.tests.app_module_progress_bar import app_progress_bar_test, \
    app_progress_bar_indeterminate_test
from tornado_websockets.tests.test_websocket import WebSocketBaseTestCase, TestWebSocketHandler, SLEEPING_TIME
from tornado_websockets.websocket import WebSocket


class TestModuleProgressBar(TestCase):
    def test_constructor_default_values(self):
        progress_bar = ProgressBar(WebSocket('test'))

        self.assertEqual(progress_bar.min, 0)
        self.assertEqual(progress_bar.max, 100)
        self.assertEqual(progress_bar.value, 0)
        self.assertFalse(progress_bar.indeterminate)
        self.assertIsInstance(progress_bar.websocket, WebSocket)

    def test_constructor_if_indeterminate(self):
        progress_bar = ProgressBar(WebSocket('test'), min=1234, max=1234)

        self.assertTrue(progress_bar.indeterminate)

    def test_constructor_if_not_indeterminate(self):
        progress_bar = ProgressBar(WebSocket('test'))

        self.assertFalse(progress_bar.indeterminate)

    def test_constructor_websocket_instance(self):
        with self.assertRaises(ValueError) as e:
            progress_bar = ProgressBar("not WebSocket instance")

        self.assertEqual(str(e.exception), "`websocket` parameter should be an instance of WebSocket class")

    def test_constructor_max_lt_min(self):
        with self.assertRaises(ValueError) as e:
            progress_bar = ProgressBar(WebSocket('test'), min=0, max=-50)

        self.assertEqual(str(e.exception), "`max` value (-50) can not be lower than `min` value (0).")

    def test_is_done(self):
        progress_bar = ProgressBar(WebSocket('test'))
        self.assertFalse(progress_bar.is_done())

        progress_bar.value = progress_bar.max
        self.assertTrue(progress_bar.is_done())

        progress_bar = ProgressBar(WebSocket('test'), min=0, max=0)
        self.assertFalse(progress_bar.is_done())


class TestModuleProgressBarWebSocket(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()

        return Application([
            ('/ws/my_progress_bar', TestWebSocketHandler, {
                'websocket': app_progress_bar_test.websocket,
                'close_future': self.close_future
            }),
        ])

    def setUp(self):
        super(TestModuleProgressBarWebSocket, self).setUp()
        app_progress_bar_test.reset()

    @gen_test
    def test_method_reset(self):
        self.assertEqual(app_progress_bar_test.value, app_progress_bar_test.min)

        app_progress_bar_test.value = 20
        app_progress_bar_test.reset()
        self.assertEqual(app_progress_bar_test.value, app_progress_bar_test.min)

    @gen_test
    def test_method_on(self):
        self.assertIsNone(app_progress_bar_test.websocket.events.get('module_progressbar_my_event'))

        @app_progress_bar_test.on
        def my_event():
            pass

        self.assertTrue(callable(app_progress_bar_test.websocket.events.get('module_progressbar_my_event')))

    @gen_test
    def test_property_value(self):
        app_progress_bar_test.value = 20
        self.assertEqual(app_progress_bar_test.value, 20)

        with self.assertRaises(ValueError):
            app_progress_bar_test.value = app_progress_bar_test.min - 1

        with self.assertRaises(ValueError):
            app_progress_bar_test.value = app_progress_bar_test.max + 1

    @gen_test
    def test_property_context(self):
        self.assertIsNone(app_progress_bar_test.context)
        self.assertIsNone(app_progress_bar_test.websocket.context)

        app_progress_bar_test.context = 'Not a really an object.'
        self.assertEqual(app_progress_bar_test.context, 'Not a really an object.')
        self.assertEqual(app_progress_bar_test.websocket.context, 'Not a really an object.')

    @gen_test
    def test_event_init(self):
        ws = yield self.ws_connect('/ws/my_progress_bar')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_init')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_init',
            'data': {
                'min': 0,
                'max': 100,
                'value': 0,
                'indeterminate': False
            }
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_init')

        self.close(ws)

    @gen_test
    def test_method_tick_and_event_update(self):
        ws = yield self.ws_connect('/ws/my_progress_bar')

        # --- Can't make a function for this q_q
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_init')
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_init')
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_init')
        # --- q_q

        app_progress_bar_test.reset()
        self.assertEqual(app_progress_bar_test.value, app_progress_bar_test.min)

        # 1st tick without label
        app_progress_bar_test.tick()
        self.assertEqual(app_progress_bar_test.value, app_progress_bar_test.min + 1)

        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_update')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_update',
            'data': {'value': app_progress_bar_test.min + 1}
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_update')

        # 2nd tick with label
        app_progress_bar_test.tick('My label :-)')
        self.assertEqual(app_progress_bar_test.value, app_progress_bar_test.min + 2)

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_update')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_update',
            'data': {
                'value': app_progress_bar_test.min + 2,
                'label': 'My label :-)'
            }
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_update')

        self.close(ws)

    @gen_test
    def test_method_emit_done(self):
        ws = yield self.ws_connect('/ws/my_progress_bar')

        # --- Can't make a function for this q_q
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_init')
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_init')
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_init')
        # --- q_q

        app_progress_bar_test.reset()
        app_progress_bar_test.value = 99
        self.assertEqual(app_progress_bar_test.value, 99)
        self.assertEqual(app_progress_bar_test.max, 100)

        # Aaaaaaaaaaaaaaaaaaaand it's done
        app_progress_bar_test.tick()

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_update')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_update',
            'data': {'value': 100}
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_update')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_done')

        self.close(ws)


class TestModuleProgressBarIndeterminateWebSocket(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()

        return Application([
            ('/ws/my_indeterminate_progress_bar', TestWebSocketHandler, {
                'websocket': app_progress_bar_indeterminate_test.websocket,
                'close_future': self.close_future
            })
        ])

    def setUp(self):
        super(TestModuleProgressBarIndeterminateWebSocket, self).setUp()
        app_progress_bar_indeterminate_test.reset()

    @gen_test
    def test_event_init(self):
        ws = yield self.ws_connect('/ws/my_indeterminate_progress_bar')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_init')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_init',
            'data': {
                'indeterminate': True
            }
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_init')

        self.close(ws)

    @gen_test
    def test_method_tick_and_event_update(self):
        ws = yield self.ws_connect('/ws/my_indeterminate_progress_bar')

        # --- Can't make a function for this q_q
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_init')
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_init')
        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_init')
        # --- q_q

        self.assertTrue(app_progress_bar_indeterminate_test.indeterminate)

        # 1st tick without label
        self.assertEqual(app_progress_bar_indeterminate_test.value, app_progress_bar_indeterminate_test.min)
        app_progress_bar_indeterminate_test.tick()
        self.assertEqual(app_progress_bar_indeterminate_test.value, app_progress_bar_indeterminate_test.min)

        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_update')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_update',
            'data': {}
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_update')

        # 2nd tick with label
        self.assertEqual(app_progress_bar_indeterminate_test.value, app_progress_bar_indeterminate_test.min)
        app_progress_bar_indeterminate_test.tick('My label :-)')
        self.assertEqual(app_progress_bar_indeterminate_test.value, app_progress_bar_indeterminate_test.min)

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_before_update')

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertDictEqual(json_decode(response), {
            'event': 'module_progressbar_update',
            'data': {'label': 'My label :-)'}
        })

        time.sleep(SLEEPING_TIME)
        response = yield ws.read_message()
        self.assertEqual(json_decode(response).get('event'), 'module_progressbar_after_update')

        self.close(ws)
