import pytest
import mock

from django.template import Template, Context

class DescribeMethodFilter:
    """Tests for the `method` filter"""
    @classmethod
    def setup_class(cls):
        cls.request = mock.Mock()
        cls.template = Template('''
            {% load custom_filters %}
            {{ test|method:"test_method" }}
        ''')

    def it_recognizes_callable(self):
        class Test:
            def test_method(self):
                return 'test output'

        context = Context({ 'test': Test() })
        template = self.template.render(context)
        assert 'bound method Test.test_method' in template

    def it_recognizes_not_callable(self):
        class Test:
            pass

        context = Context({ 'test': Test() })
        template = self.template.render(context)
        assert 'has no method test_method' in template

class DescribeWithFilter:
    """Tests for the `with` filter"""
    @classmethod
    def setup_class(cls):
        cls.request = mock.Mock()
        cls.template = Template('''
            {% load custom_filters %}
            {{ test|method:"test_method"|with:my_string }}
        ''')

    def it_recognizes_callable(self):
        class Test:
            def test_method(self):
                return 'test output'

        context = Context({ 'test': Test(), 'my_string': 'hello' })
        template = self.template.render(context)
        assert 'functools.partial' in template

    def it_recognizes_not_callable(self):
        self.template = Template('''
            {% load custom_filters %}
            {{ test|with:my_string }}
        ''')
        context = Context({ 'test': 'testing', 'my_string': 'hello' })
        template = self.template.render(context)
        assert 'testing is not callable' in template

class DescribeCallFilter:
    """Tests for the `call` filter"""
    @classmethod
    def setup_class(cls):
        cls.request = mock.Mock()
        cls.template = Template('''
            {% load custom_filters %}
            {{ test|method:"test_method"|call }}
        ''')

    def it_recognizes_callable(self):
        class Test:
            def test_method(self):
                return 'test output'

        context = Context({ 'test': Test(), 'my_string': 'hello' })
        template = self.template.render(context)
        assert template.strip() == 'test output'

    def it_recognizes_not_callable(self):
        self.template = Template('''
            {% load custom_filters %}
            {{ test|call }}
        ''')
        context = Context({ 'test': 'testing', 'my_string': 'hello' })
        template = self.template.render(context)
        assert 'testing is not callable' in template
