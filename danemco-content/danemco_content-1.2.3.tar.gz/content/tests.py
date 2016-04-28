import datetime

from django.contrib.auth import get_user_model
from django.http.response import HttpResponse, HttpResponseNotFound
from django.template.base import Template
from django.template.context import Context
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.utils import timezone

from content.middleware import PageFallbackMiddleware
from content.models import Page, Section, Snippet


User = get_user_model()

class ContentTestCase(TestCase):

    def setUp(self):
        self.section = Section.objects.create(name="foozle")

    def test_view(self):

        # sanity check
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

        Page.objects.create(url="/", content="Foo")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_required_anonymous(self):
        Page.objects.create(url="/", content="Foo", registration_required=True)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_login_required_logged(self):
        Page.objects.create(url="/", content="Foo", registration_required=True)
        User.objects.create_user("test", "", "test")
        self.client.login(username="test", password="test")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_middleware(self):
        middleware = PageFallbackMiddleware()
        factory = RequestFactory()

        # no page has been created
        response = middleware.process_response(
            factory.get("/test/"),
            HttpResponseNotFound()
        )

        self.assertEqual(response.status_code, 404)

        # insert page
        Page.objects.create(url="/test/")

        response = middleware.process_response(
            factory.get("/test/"),
            HttpResponseNotFound()
        )
        self.assertEqual(response.status_code, 200)

    def test_snippet(self):

        self.assertEqual(Section.objects.filter(name="foo").count(), 0)

        template = Template("{% load content_tags %}{% snippet 'foo' %}")
        self.assertEqual(template.render(Context()), "")

        # should have created section
        self.assertEqual(Section.objects.filter(name="foo").count(), 1)

        Snippet.objects.create(
            section=Section.objects.get(name="foo"),
            content="foo"
        )

        self.assertEqual(template.render(Context()), "foo")

    def test_publish_soon_snippet(self):

        template = Template("{% load content_tags %}{% snippet 'foozle' %}")

        # should have created section
        Snippet.objects.create(
            section=self.section,
            content="foo1"
        )
        Snippet.objects.create(
            section=self.section,
            publish=timezone.now() + datetime.timedelta(hours=1),
            content="foo2"
        )

        self.assertEqual(template.render(Context()), "foo1")

    def test_published_snippet(self):

        template = Template("{% load content_tags %}{% snippet 'foozle' %}")

        # should have created section
        Snippet.objects.create(
            section=self.section,
            content="foo1"
        )
        Snippet.objects.create(
            section=self.section,
            publish=timezone.now() - datetime.timedelta(hours=1),
            content="foo2"
        )
        Snippet.objects.create(
            section=self.section,
            publish=timezone.now() - datetime.timedelta(hours=2),
            content="foo3"
        )

        self.assertEqual(template.render(Context()), "foo2")

    def test_expire_soon_snippet(self):

        template = Template("{% load content_tags %}{% snippet 'foozle' %}")

        # should have created section
        Snippet.objects.create(
            section=self.section,
            content="foo1"
        )
        Snippet.objects.create(
            section=self.section,
            expire=timezone.now() + datetime.timedelta(hours=1),
            content="foo2"
        )
        Snippet.objects.create(
            section=self.section,
            expire=timezone.now() + datetime.timedelta(hours=2),
            content="foo3"
        )
        # also takes precedence over publish time
        Snippet.objects.create(
            section=self.section,
            publish=timezone.now() - datetime.timedelta(hours=2),
            content="foo4"
        )

        self.assertEqual(template.render(Context()), "foo2")

    def test_expired_snippet(self):

        template = Template("{% load content_tags %}{% snippet 'foozle' %}")

        # should have created section
        Snippet.objects.create(
            section=self.section,
            content="foo1"
        )
        Snippet.objects.create(
            section=self.section,
            expire=timezone.now() - datetime.timedelta(hours=1),
            content="foo2"
        )

        self.assertEqual(template.render(Context()), "foo1")
