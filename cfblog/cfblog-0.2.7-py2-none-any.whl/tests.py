# coding=utf-8
import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings
from django.utils.decorators import method_decorator

from .models import Content
from .utils import NAMESPACE_DELIMITER, parse_cms_template


class BaseTests(SimpleTestCase):
    cms_context = {}
    template_context = None

    def setUp(self):
        self.html = """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                        hello
                    </h1>
                </body>
            </html>
        """

    @property
    def output(self):
        return parse_cms_template(self.html, self.cms_context, public=True,
                                  template_context=self.template_context)


class BasicTagTests(BaseTests):

    def test_empty_context(self):
        self.cms_context = {}
        self.assertHTMLEqual(self.html, self.output)

    def test_data_cms_content(self):
        self.cms_context = {"h1": "foo"}
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                        foo
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_data_cms_attr(self):
        self.cms_context = {"id": "new_id"}
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="new_id">
                        hello
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_data_cms_replace(self):
        self.html = """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig"
                        data-cms-replace>
                    <div data-cms-content="content" data-cms-attr="id:div_id"
                        id="replaced">
                            new content
                    </div>
                    </h1>
                </body>
            </html>
            """
        self.cms_context = {}
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                </body>
            </html>
            """,
            self.output
        )
        self.cms_context = {'h1': '<div>replaced h1</div>'}
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <div>replaced h1</div>
                </body>
            </html>
            """,
            self.output
        )


class MultiLevelTagTests(BaseTests):
    def test_single_level_data(self):
        self.cms_context = {'h1': '<div data-cms-content="text"></div>'}
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-content="text"></div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_multi_level_data(self):
        self.cms_context = {
            'h1': '<div data-cms-content="text"></div>',
            'h1' + NAMESPACE_DELIMITER + 'text': 'replaced'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-content="text">replaced</div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_single_level_complete_data(self):
        self.cms_context = {
            'h1': '<div data-cms-attr="id:div_id" id="default">hi</div>',
            'h1' + NAMESPACE_DELIMITER + 'div_id': 'replaced'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-attr="id:div_id" id="replaced">hi</div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_multi_level_complete_data(self):
        self.cms_context = {
            'h1': (
                '<div data-cms-content="content" '
                'data-cms-attr="id:div_id" id="default">hi</div>'
            ),
            'h1' + NAMESPACE_DELIMITER + 'div_id': 'replaced',
            'h1' + NAMESPACE_DELIMITER + 'content': 'new content'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-content="content" data-cms-attr="id:div_id"
                        id="replaced">
                            new content
                    </div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )


class CMSTests(BaseTests):
    def test_snippet_insertions(self):
        self.cms_context = {
            'h1': '<div data-cms-include="namespace:cms_templates/snippet">'
                  '</div>'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet"
                        data-cms-namespace="namespace">
                            hehehe
                            <div data-cms-content="md:text">Hi</div>
                    </div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_snippet_insertions_data(self):
        self.cms_context = {
            'h1': '<div data-cms-include="namespace:cms_templates/snippet">'
                  '</div>',
            NAMESPACE_DELIMITER.join(
                ('h1', 'namespace', 'text')
            ): '##Heading##'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet"
                        data-cms-namespace="namespace">
                            hehehe
                            <div data-cms-content="md:text">
                                <h2>Heading</h2>
                            </div>
                    </div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

        self.cms_context = {
            'h1': '<div '
                  'data-cms-include="namespace:cms_templates/snippet_2">'
                  '</div>',
            NAMESPACE_DELIMITER.join(
                ('h1', 'namespace', 'text2')
            ): '##Heading##'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet_2"
                        data-cms-namespace="namespace">
                        <div data-cms-content="md:text2"><h2>Heading</h2></div>
                    </div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_template_context(self):
        self.cms_context = {
            'h1': '<div data-cms-include="namespace:cms_templates/snippet">'
                  '</div>',
            NAMESPACE_DELIMITER.join(
                ('h1', 'namespace', 'text')
            ): '##Heading##'
        }
        self.template_context = {
            'greeting': 'hello'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet"
                        data-cms-namespace="namespace">
                            hello
                            <div data-cms-content="md:text">
                                <h2>Heading</h2>
                            </div>
                    </div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )

    def test_markdown(self):
        self.html = """
        <html>
            <head>
            </head>
            <body>
                <h1 data-cms-content="md:h1" data-cms-attr="id:id" id="orig">
                    hello
                </h1>
            </body>
        </html>
        """
        self.cms_context = {
            'h1': '##Heading##\n'
                  '<div '
                  'data-cms-include="namespace:cms_templates/snippet_2">'
                  '</div>',
            NAMESPACE_DELIMITER.join(
                ('h1', 'namespace', 'text2')
            ): '##Heading##'
        }
        self.assertHTMLEqual(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="md:h1" data-cms-attr="id:id"
                        id="orig">
                    <h2>Heading</h2>
                    <div data-cms-include="cms_templates/snippet_2"
                        data-cms-namespace="namespace">
                            <div data-cms-content="md:text2">
                                <h2>Heading</h2>
                            </div>
                    </div>
                    </h1>
                </body>
            </html>
            """,
            self.output
        )


class RegressionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        editor_credentials = {
            User.USERNAME_FIELD: 'editor',
            'password': 'test123'
        }
        author_credentials = {
            User.USERNAME_FIELD: 'author',
            'password': 'test123'
        }
        editor = User.objects.create_user(**editor_credentials)
        author = User.objects.create_user(**author_credentials)
        # We are explicitly setting is_active because of django 1.8
        editor.is_active = True
        editor.save()
        author.is_active = True
        author.save()
        edit_permission = Permission.objects.get(
            codename='change_content',
            content_type__app_label='cfblog'
        )
        publish_permission = Permission.objects.get(
            codename='can_publish',
            content_type__app_label='cfblog'
        )
        author.user_permissions.add(publish_permission)
        editor.user_permissions.add(edit_permission)
        cls.author = author
        cls.editor = editor
        cls.author_client = cls.client_class()
        cls.author_client.login(**author_credentials)
        cls.editor_client = cls.client_class()
        cls.editor_client.login(**editor_credentials)

    def setUp(self):
        cms_page, _ = Content.objects.get_or_create(
            url='/test-golbfc/',
            template="cms_templates/template_1.html",
            category_id=1,
            author=self.author
        )
        self.cms_page = cms_page

    def test_unpublished_url(self):
        self.cms_page.status = Content.DRAFT
        self.cms_page.save()
        response = self.client.get(self.cms_page.url)
        self.assertEqual(response.status_code, 404)
        response = self.editor_client.get(self.cms_page.url)
        self.assertEqual(response.status_code, 200)
        response = self.author_client.get(self.cms_page.url)
        self.assertEqual(response.status_code, 200)

    def test_published_url(self):
        self.cms_page.status = Content.PUBLIC
        self.cms_page.save()
        response = self.client.get(self.cms_page.url)
        self.assertEqual(response.status_code, 200)
        response = self.editor_client.get(self.cms_page.url)
        self.assertEqual(response.status_code, 200)
        response = self.author_client.get(self.cms_page.url)
        self.assertEqual(response.status_code, 200)

    @method_decorator(override_settings(ROOT_URLCONF=()))
    def test_custom_url_conf(self):
        # response should be served by the middleware
        self.test_published_url()
        self.test_unpublished_url()

    def test_editor_cannot_publish(self):
        response1 = self.editor_client.post(
            path='/cms/ajax/save/publish/',
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response1.status_code, 403)

    def test_author_can_publish(self):
        response1 = self.author_client.post(
            path='/cms/ajax/save/publish/',
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertNotEqual(response1.status_code, 403)

    def test_versioning(self):

        content = json.dumps({
            "body": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "body_attr": "random data",
            "decrp": "Hi!!",
            "title": "Hello World!!!"
        })
        draft_time = self.cms_page.modified_on + datetime.timedelta(minutes=5)
        data = {
            'auth_data': content,
            'draft_modified': draft_time.isoformat(),
            'cms_page_id': self.cms_page.id
        }

        response1 = self.author_client.post(
            path='/cms/ajax/save/publish/',
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(json.loads(response1.content)['success'])

        draft_time = self.cms_page.modified_on - datetime.timedelta(minutes=5)
        data['draft_modified'] = draft_time.isoformat()
        response2 = self.author_client.post(
            path='/cms/ajax/save/publish/',
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(json.loads(response2.content)['success'])
        self.assertTrue(json.loads(response2.content)['draft_error'])
