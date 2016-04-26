import json
import datetime

from django.test import TestCase, Client
from django.apps import apps
from django.conf import settings

from .models import Content
from .utils import parse_cms_template, NAMESPACE_DELIMITER

__author__ = 'vinay'


class CMSTests(TestCase):
    def test_basic_features(self):
        html = """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">hello</h1>
                </body>
            </html>
        """
        out = parse_cms_template(html, {})
        self.assertHTMLEqual(html, out)

        out = parse_cms_template(html, {"h1": "foo"})
        self.assertHTMLEqual(
            out, """
                <html>
                    <head>
                    </head>
                    <body>
                        <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">foo</h1>
                    </body>
                </html>
            """
        )

        self.assertHTMLEqual(
            parse_cms_template(html, {"id": "new_id"}),
            """
                <html>
                    <head>
                    </head>
                    <body>
                        <h1 data-cms-content="h1" data-cms-attr="id:id" id="new_id">hello</h1>
                    </body>
                </html>
            """
        )

    def test_advanced_features(self):
        html = """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">hello</h1>
                </body>
            </html>
        """
        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-content="text"></div>'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-content="text"></div>
                    </h1>
                </body>
            </html>
        """)

        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-content="text"></div>',
             'h1' + NAMESPACE_DELIMITER + 'text': 'replaced'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-content="text">replaced</div>
                    </h1>
                </body>
            </html>
        """)

        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-attr="id:div_id" id="default">hi</div>',
             'h1' + NAMESPACE_DELIMITER + 'div_id': 'replaced'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-attr="id:div_id" id="replaced">hi</div>
                    </h1>
                </body>
            </html>
        """)

        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-content="content" data-cms-attr="id:div_id" id="default">hi</div>',
             'h1' + NAMESPACE_DELIMITER + 'div_id': 'replaced',
             'h1' + NAMESPACE_DELIMITER + 'content': 'new content'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-content="content" data-cms-attr="id:div_id" id="replaced">new content</div>
                    </h1>
                </body>
            </html>
        """)

    def test_snippet_insertions(self):
        html = """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">hello</h1>
                </body>
            </html>
        """
        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-include="namespace:cms_templates/snippet"></div>'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet" data-cms-namespace="namespace">
                    hehehe
                    <div data-cms-content="md:text">Hi</div>
                    </div>
                    </h1>
                </body>
            </html>
        """)

        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-include="namespace:cms_templates/snippet"></div>',
             NAMESPACE_DELIMITER.join(('h1', 'namespace', 'text')): '##Heading##'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet" data-cms-namespace="namespace">
                    hehehe
                    <div data-cms-content="md:text"><h2>Heading</h2></div>
                    </div>
                    </h1>
                </body>
            </html>
        """)

        out = parse_cms_template(
            html,
            {'h1': '<div data-cms-include="namespace:cms_templates/snippet_2"></div>',
             NAMESPACE_DELIMITER.join(('h1', 'namespace', 'text2')): '##Heading##'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    <div data-cms-include="cms_templates/snippet_2" data-cms-namespace="namespace">
                    <div data-cms-content="md:text2"><h2>Heading</h2></div>
                    </div>
                    </h1>
                </body>
            </html>
        """)

        out = parse_cms_template(
            html,
            {'h1': '##Heading##\n'
                   '<div data-cms-include="namespace:cms_templates/snippet_2"></div>',
             NAMESPACE_DELIMITER.join(('h1', 'namespace', 'text2')): '##Heading##'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="h1" data-cms-attr="id:id" id="orig">
                    ##Heading##
                    <div data-cms-include="cms_templates/snippet_2" data-cms-namespace="namespace">
                    <div data-cms-content="md:text2"><h2>Heading</h2></div>
                    </div>
                    </h1>
                </body>
            </html>
        """)

        html = """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="md:h1" data-cms-attr="id:id" id="orig">hello</h1>
                </body>
            </html>
        """
        out = parse_cms_template(
            html,
            {'h1': '##Heading##\n'
                   '<div data-cms-include="namespace:cms_templates/snippet_2"></div>',
             NAMESPACE_DELIMITER.join(('h1', 'namespace', 'text2')): '##Heading##'}
        )
        self.assertHTMLEqual(out, """
            <html>
                <head>
                </head>
                <body>
                    <h1 data-cms-content="md:h1" data-cms-attr="id:id" id="orig">
                    <h2>Heading</h2>
                    <div data-cms-include="cms_templates/snippet_2" data-cms-namespace="namespace">
                    <div data-cms-content="md:text2"><h2>Heading</h2></div>
                    </div>
                    </h1>
                </body>
            </html>
        """)

    def test_versioning(self):
        client = Client()
        app_label, model = settings.AUTH_USER_MODEL.split('.', 1)
        User = apps.get_model(app_label, model)
        user = User.objects.create_superuser(**{
            User.USERNAME_FIELD: 'test-golbfc',
            'email': 'test@test.com',
            'password': 'test123'}
        )
        cms_page, _ = Content.objects.get_or_create(
            url='/test-golbfc/',
            template="cms_templates/template_1.html",
            category_id=1,
            author=user
        )

        content = """
                    {
                      "body":"ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                      "body_attr":"random data",
                      "decrp":"Hi!!",
                      "title":"Hello World!!!"
                    }
                  """
        t = (cms_page.modified_on + datetime.timedelta(minutes=5)).isoformat()
        data = {
                'auth_data': content,
                'draft_modified': t,
                'cms_page_id': cms_page.id
                }
        self.assertTrue(
            client.login(**{
                User.USERNAME_FIELD: 'test-golbfc', 'password': 'test123'
            })
        )
        response1 = client.post(
            path='/cms/ajax/save/publish/',
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(json.loads(response1.content)['success'])

        data['draft_modified'] = '2016-04-07T13:45:35.322Z'
        response2 = client.post(
            path='/cms/ajax/save/publish/',
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(json.loads(response2.content)['success'])
        self.assertTrue(json.loads(response2.content)['draft_error'])
