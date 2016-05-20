from __future__ import unicode_literals
from __future__ import print_function

import unittest

from django.db.utils import ProgrammingError, InterfaceError
from mock import patch, Mock
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor import MiscSensor

class MiscSensorTest(unittest.TestCase):

    def create_default_sensor_test(self):
        sensor = MiscSensor()
        self.assertFalse(sensor.csrf_exception_enabled)
        self.assertFalse(sensor.sql_exception_enabled)

    def create_enabled_sensor_test(self):
        sensor = MiscSensor({
            "csrf_exception_enabled": True,
            "sql_exception_enabled": True
        })
        self.assertTrue(sensor.csrf_exception_enabled)
        self.assertTrue(sensor.sql_exception_enabled)

    def with_disabled_sensor_csrf_rejected_test(self):
        sensor = MiscSensor({"csrf_exception_enabled": False})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.misc_sensor.sendEvent') as patched_send_event:
            sensor.csrf_rejected(meta, "Missing CSRF")
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_csrf_rejected_test(self):
        sensor = MiscSensor({"csrf_exception_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.misc_sensor.sendEvent') as patched_send_event:
            sensor.csrf_rejected(meta, "Missing CSRF")
            patched_send_event.assert_called_once_with(meta, "excsrf", None, None, payload=None)

    def with_disabled_sensor_sql_exception_test(self):
        sensor = MiscSensor({"sql_exception_enabled": False})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.misc_sensor.sendEvent') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                meta = Mock()
                exc_type = Mock()
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, meta,  exc_type, exc_value, tb)
                self.assertFalse(patched_send_event.called)
                self.assertFalse(patched_print_tb.called)

    def with_enabled_sensor_sql_exception_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.misc_sensor.sendEvent') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                exc_type = ProgrammingError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, meta,  exc_type, exc_value, tb)
                patched_send_event.assert_called_once_with(meta, "exsql", None, None, payload='printed stack')
                patched_print_tb.assert_called_once_with(tb)

    def with_enabled_sensor_sql_exception_interface_error_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True})
        meta = AppSensorMeta(
            "remote_addr",
            "request_method",
            "abosolute_uri",
            "23947",
            session_id="session_id",
            user_id="user_id"
        )
        with patch('tcell_agent.policies.appsensor.misc_sensor.sendEvent') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                exc_type = InterfaceError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, meta,  exc_type, exc_value, tb)
                self.assertFalse(patched_send_event.called)
                self.assertFalse(patched_print_tb.called)
