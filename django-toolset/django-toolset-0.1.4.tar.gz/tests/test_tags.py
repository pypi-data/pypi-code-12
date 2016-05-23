import pytest
from mock import Mock

from django.core.urlresolvers import NoReverseMatch
from django.template import Template, Context

@pytest.mark.urls('tests.testapp.urls')
class DescribeActiveTag:
    """Tests for the `active` templatetag"""
    @classmethod
    def setup_class(cls):
        cls.request = Mock()
        cls.request.path = '/login/'
        cls.context = Context({ 'request': cls.request, })

    def make_template_for(self, url):
        return Template("{% load custom_tags %}{% active '" + url + "' %}")

    def it_knows_page_is_current(self):
        template = self.make_template_for('login').render(self.context)
        assert template == 'active'

    def it_knows_page_is_not_current(self):
        template = self.make_template_for('home').render(self.context)
        assert template == ''

    def it_knows_page_is_current_from_regex(self):
        template = self.make_template_for('^/login/$').render(self.context)
        assert template == 'active'

    def it_can_customize_class_name(self):
        template = Template("{% load custom_tags %}{% active 'login' class_name='current' %}")
        template = template.render(self.context)
        assert template == 'current'
