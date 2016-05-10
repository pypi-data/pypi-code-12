import uuid

from infosessions.session import SessionStore
from django.test import TestCase


class SessionTestCase(TestCase):
    def setUp(self):
        self.session = SessionStore()

    def test_modified(self):
        self.assertFalse(self.session.modified)
        self.session.create()
        self.session['kek'] = 'pek'
        self.assertTrue(self.session.modified)
        self.assertIsNotNone(self.session.session_key)


class SessionPersistenceTestCase(TestCase):
    def setUp(self):
        self.key = 'key'
        self.value = str(uuid.uuid4())
        session = SessionStore()
        session[self.key] = self.value
        session.save()
        self.session_key = session.session_key

    def test_key_exist(self):
        s = SessionStore()
        self.assertTrue(s.exists(self.session_key))

    def test_delete(self):
        s = SessionStore(self.session_key)
        s.delete()
        self.assertFalse(s.exists(self.session_key))

    def test_value_changed(self):
        session = SessionStore(self.session_key)
        self.assertEqual(session[self.key], self.value)