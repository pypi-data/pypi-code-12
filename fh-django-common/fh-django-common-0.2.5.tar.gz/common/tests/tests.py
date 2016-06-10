import datetime

from django.template import Template, Context
from django.test import TestCase, RequestFactory

from models import TestDateTimeModel


class TagsTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_url_replace(self):
        request = self.request_factory.get('/test_url_replace?foo=bar&page=1')
        template = Template("{% load common %} <a href=\"?{% url_replace request 'page' '2' %}\"></a>")  # nopep8
        response = template.render(Context({'request': request}))
        self.assertIn('page=2', response)
        self.assertNotIn('page=1', response)
        self.assertIn('foo=bar', response)


class ModelTestCase(TestCase):

    def test_datetime_model_mixin(self):
        test_dt = TestDateTimeModel()

        self.assertIsNone(test_dt.created_at)
        self.assertIsNone(test_dt.updated_at)

        test_dt.save()

        self.assertIsNotNone(test_dt.created_at)
        self.assertIsNotNone(test_dt.updated_at)
        self.assertIsInstance(test_dt.created_at, datetime.datetime)
        self.assertIsInstance(test_dt.updated_at, datetime.datetime)
