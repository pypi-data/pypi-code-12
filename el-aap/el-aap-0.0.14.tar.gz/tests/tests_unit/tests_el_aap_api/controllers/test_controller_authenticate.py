__author__ = 'schlitzer'

from unittest import TestCase
from unittest.mock import Mock, patch, call

from el_aap_api.controllers import authenticate
from el_aap_api.errors import SessionError


class TestUnitControllerAuthenticate(TestCase):
    def setUp(self):
        request_patcher = patch('el_aap_api.controllers.authenticate.request', autospec=False)
        self.request = request_patcher.start()

        response_patcher = patch('el_aap_api.controllers.authenticate.response', autospec=False)
        self.response = response_patcher.start()

    def test_create(self):
        expected = {
            '_id': 'session_id',
            'token': 'session_token'
        }
        self.request.json = {
            "user": "test_user",
            "password": "password"
        }

        m_sessions = Mock()
        m_sessions.create.return_value = expected
        m_users = Mock()
        m_users.check_credentials.return_value = 'test_user'

        result = authenticate.create(m_users, m_sessions)

        m_users.check_credentials.assert_called_with(self.request.json)
        m_sessions.create.assert_called_with('test_user')
        self.response.set_cookie.assert_has_calls([
            call('sid', 'session_id'),
            call('token', 'session_token')
        ])
        self.assertEqual(self.response.status, 201)
        self.assertEquals(result, expected)

    def test_delete(self):
        m_sessions = Mock()
        m_aa = Mock()
        m_aa.get_session.return_value = {
            '_id': 'session_id',
            'token': 'session_token'
        }
        authenticate.delete(m_sessions, m_aa)
        m_aa.get_session.assert_called_with()
        self.response.delete_cookie.assert_has_calls([
            call('_id'),
            call('token')
        ])
        m_sessions.delete.assert_called_with('session_id')

    def test_delete_invalid_session(self):
        m_sessions = Mock()
        m_aa = Mock()
        m_aa.get_session.side_effect = SessionError
        self.assertRaises(SessionError, authenticate.delete, m_sessions, m_aa)
        m_aa.get_session.assert_called_with()
        self.response.delete_cookie.assert_has_calls([
            call('_id'),
            call('token')
        ])
