# -*- coding: utf-8 -*-
from pytest import fixture
import colander


@fixture
def renderer():
    from deform.tests.test_widget import DummyRenderer
    return DummyRenderer()


@fixture
def schema():
    from deform.tests.test_widget import DummySchema
    return DummySchema()


@fixture
def field(schema, renderer):
    from deform.tests.test_widget import DummyField
    return DummyField(schema, renderer)


class TestMarkdownTextAreaWidget:

    def make_one(self, **kw):
        from . import MarkdownTextAreaWidget
        return MarkdownTextAreaWidget(**kw)

    def test_serialize_null(self, field):
        inst = self.make_one()
        inst.serialize(field, colander.null)
        assert field.renderer.template == inst.template
        assert field.renderer.kw['field'] == field
        assert field.renderer.kw['cstruct'] == ''

    def test_serialize_none(self, field):
        inst = self.make_one()
        inst.serialize(field, None)
        assert field.renderer.template == inst.template
        assert field.renderer.kw['field'] == field
        assert field.renderer.kw['cstruct'] == ''

    def test_serialize_not_null(self, field):
        inst = self.make_one()
        inst.serialize(field, 'abc')
        assert field.renderer.kw['cstruct'] == 'abc'

    def test_serialize_readonly(self, field):
        inst = self.make_one()
        field.schema = schema
        inst.serialize(field, None, readonly=True)
        assert field.renderer.template == inst.readonly_template

    def test_serialize_default_and_custom_options(self, field):
        import json
        inst = self.make_one()
        inst.serialize(field, 'abc', options={'custom': '1'})
        result = field.renderer.kw['simplemde_options']
        result_options = json.loads(result)
        assert result_options['height'] == 240
        assert result_options['custom'] == '1'

    def test_serialize_autosave_default_option(self, field, monkeypatch):
        import json
        inst = self.make_one()
        inst.serialize(field, 'abc')
        result = field.renderer.kw['simplemde_options']
        result_options = json.loads(result)
        assert result_options['autosave']['enabled']
        assert result_options['autosave']['uniqueid']

    def test_deserialize_strip(self, field):
        inst = self.make_one()
        result = inst.deserialize(field, ' abc ')
        assert result == 'abc'

    def test_deserialize_no_strip(self, field):
        inst = self.make_one(strip=False)
        result = inst.deserialize(field, ' abc ')
        assert result == ' abc '

    def test_deserialize_null(self, field):
        inst = self.make_one(strip=False)
        result = inst.deserialize(field, colander.null)
        assert result is colander.null

    def test_deserialize_emptystring(self, field):
        inst = self.make_one()
        result = inst.deserialize(field, '')
        assert result is colander.null


def test_add_default_resources():
    from deform.widget import default_resource_registry
    assert 'simplemde' in default_resource_registry.registry
