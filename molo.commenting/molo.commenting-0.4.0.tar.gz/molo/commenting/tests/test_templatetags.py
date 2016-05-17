from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.template import Template, Context

from molo.commenting.models import MoloComment
from molo.commenting.forms import MoloCommentForm


class GetMoloCommentsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)

        for i in range(10):
            MoloComment.objects.create(
                content_type=self.content_type,
                object_pk=self.user.pk,
                content_object=self.user,
                site=Site.objects.get_current(),
                user=self.user,
                comment='comment %s' % (i,),
                submit_date=datetime.now())

    def test_template_tags_default(self):
        template = Template("""
        {% load molo_commenting_tags mptt_tags %}
        {% get_molo_comments for object as comments %}
        {% for comment in comments %}
            {% recursetree comment %}
                {{ node.comment }}
                {{ children }}
            {% endrecursetree %}
        {% endfor %}
        """)
        output = template.render(Context({
            'object': self.user,
        }))
        self.assertFalse('comment 4' in output)
        self.assertTrue('comment 5' in output)
        self.assertTrue('comment 9' in output)

    def test_template_tags_limits(self):
        template = Template("""
        {% load molo_commenting_tags mptt_tags %}
        {% get_molo_comments for object as comments limit 2 %}
        {% for comment in comments %}
            {% recursetree comment %}
                {{ node.comment }}
                {{ children }}
            {% endrecursetree %}
        {% endfor %}
        """)
        output = template.render(Context({
            'object': self.user,
        }))
        self.assertFalse('comment 4' in output)
        self.assertFalse('comment 5' in output)
        self.assertTrue('comment 8' in output)
        self.assertTrue('comment 9' in output)

    def test_template_tags_unlimited(self):
        template = Template("""
        {% load molo_commenting_tags mptt_tags %}
        {% get_molo_comments for object as comments limit -1 %}
        {% for comment in comments %}
            {% recursetree comment %}
                {{ node.comment }}
                {{ children }}
            {% endrecursetree %}
        {% endfor %}
        """)
        output = template.render(Context({
            'object': self.user,
        }))
        self.assertTrue('comment 1' in output)
        self.assertTrue('comment 9' in output)


class GetCommentsContentObjectTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)

        for i in range(10):
            MoloComment.objects.create(
                content_type=self.content_type,
                object_pk=self.user.pk,
                content_object=self.user,
                site=Site.objects.get_current(),
                user=self.user,
                comment='comment %s' % (i,),
                submit_date=datetime.now())

    def test_get_comments_content_object(self):
        template = Template("""
        {% load molo_commenting_tags %}
        {% get_comments_content_object for form as the_object %}
        {{ the_object.email }}
        """)
        output = template.render(Context({
            'form': MoloCommentForm(self.user, data={
                'content_type': 'auth.user',
                'object_pk': self.user.pk,
            }),
        }))
        self.assertTrue('test@example.org' in output)
