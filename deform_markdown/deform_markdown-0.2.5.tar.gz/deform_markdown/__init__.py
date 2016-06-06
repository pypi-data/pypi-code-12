# -*- coding: utf-8 -*-
import json

from colander import null
from deform.widget import default_resource_registry
from deform.widget import TextAreaWidget


__version__ = '0.2.5'


class MarkdownTextAreaWidget(TextAreaWidget):
    """Renders a ``<textarea>`` widget with the `simplemde` markdown editor.

    To use this widget the `simple-markdown-editor` library must be
    provided in the page where the widget is rendered. A version of
    it is included in the ``static`` directory.
    """
    template = 'markdown'
    readonly_template = 'readonly/markdown'
    strip = True
    requirements = (('simplemde', None),)
    default_options = (('height', 240),
                       ('width', 0),
                       ('forceSync', 'true'),
                       ('indentWithTabs', 'false'),
                       ('autosave', {'enabled': 'true',
                                     'uniqueid': None,
                                     }),
                       )
    """Default options passed to simplemde."""
    options = None
    """Customize default options."""

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        kw = self._add_options(kw)
        values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **values)

    def _add_options(self, kw):
        options = dict(self.default_options)
        from datetime import datetime
        uniqueid = hash(datetime.now())
        options['autosave']['uniqueid'] = uniqueid
        options_overrides = dict(kw.get('options', self.options or {}))
        options.update(options_overrides)
        kw['simplemde_options'] = json.dumps(options)
        return kw


default_resource_registry.set_css_resources(
    'simplemde',
    None,
    'deform_markdown:static/css/simplemde.min.css')


default_resource_registry.set_js_resources(
    'simplemde',
    None,
    'deform_markdown:static/scripts/simplemde.min.js')


def includeme(config):  # pragma: no cover
    """Pyramid integration: register static view for widget resources."""
    year = 86400 * 365
    config.add_static_view('deformmarkdownstatic',
                           'deform_markdown:static',
                           cache_max_age=year)
