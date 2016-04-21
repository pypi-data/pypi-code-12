# 自定义的model renders
from django.db.models import Model, AutoField
from django.template import Template
from django.template import Context
from django.utils.safestring import mark_safe
from .forms import (
    render_form_group
)
from .renderers import BaseRenderer
from .exceptions import BootstrapError
from .utils import add_css_class
from .zui import get_model_field_renderer, get_model_renderer
from .text import text_value


def render_model(object, **kwargs):
    renderer_cls = get_model_renderer(**kwargs)
    return renderer_cls(object, **kwargs).render()


def render_model_field(object, field, **kwargs):
    """
    Render a model to Zui layout
    :param field:
    :param kwargs:
    :return:
    """
    renderer_cls = get_model_field_renderer(**kwargs)
    return renderer_cls(object, field, **kwargs).render()


class ModelRenderer(BaseRenderer):
    """
    Default form renderer
    """

    def __init__(self, object, *args, **kwargs):
        if not isinstance(object, Model):
            raise BootstrapError(
                'Parameter "object" should contain a valid Django Form.')
        self.object = object
        super(ModelRenderer, self).__init__(*args, **kwargs)
        # Handle form.empty_permitted
        # if self.form.empty_permitted:
        # self.set_required = False

    def render_fields(self):
        rendered_fields = []

        for field in self.object._meta.fields:
            rendered_fields.append(render_model_field(self.object,
                                                      field,
                                                      layout=self.layout,
                                                      form_group_class=self.form_group_class,
                                                      field_class=self.field_class,
                                                      label_class=self.label_class,
                                                      show_help=self.show_help,
                                                      exclude=self.exclude,
                                                      set_required=self.set_required,
                                                      size=self.size,
                                                      horizontal_label_class=self.horizontal_label_class,
                                                      horizontal_field_class=self.horizontal_field_class,
                                                      ))
        return '\n'.join(rendered_fields)

    def render(self):
        return self.render_fields()


class ModelFieldRenderer(BaseRenderer):
    def __init__(self, object, field, *args, **kwargs):
        self.object = object
        self.field = field
        super(ModelFieldRenderer, self).__init__(*args, **kwargs)
        self.field_help = text_value(mark_safe(field.help_text)) \
            if self.show_help and field.help_text else ''

    def append_to_field(self, html):
        help_text_and_errors = [self.field_help]
        if help_text_and_errors:
            help_html = Template(
                "{{ help_text_and_errors|join:' ' }}"
            ).render(Context({
                'field': self.field,
                'help_text_and_errors': help_text_and_errors,
                'layout': self.layout,
            }))
            html += '<span class="help-block">{help}</span>'.format(
                help=help_html)
        return html

    def get_field_class(self):
        field_class = self.field_class
        if not field_class and self.layout == 'horizontal':
            field_class = self.horizontal_field_class
        return field_class

    def wrap_field(self, html):
        field_class = self.get_field_class()
        if field_class:
            html = '<div class="{klass}"><p class="form-control-static">{html}</p></div>'.format(
                klass=field_class, html=html)
        return html

    def get_label_class(self):
        label_class = self.label_class
        if not label_class and self.layout == 'horizontal':
            label_class = add_css_class(self.horizontal_label_class, 'control-label')
        if self.layout == 'inline':
            label_class = 'sr-only'
        label_class = text_value(label_class)
        if not self.show_label:
            label_class = add_css_class(label_class, 'sr-only')
        return label_class

    def get_label(self):
        label = self.field.verbose_name
        if self.layout == 'horizontal' and not label:
            return '&#160;'
        return label

    def add_label(self, html):
        label = self.get_label()
        if label:
            html = """<label class="{label_class}">{label}</label>""".format(label_class=self.get_label_class(),
                                                                             label=label) + html
        return html

    def get_form_group_class(self):
        form_group_class = self.form_group_class

        if self.layout == 'horizontal':
            form_group_class = add_css_class(
                form_group_class, self.get_size_class(prefix='form-group'))
        return form_group_class

    def wrap_label_and_field(self, html):
        return render_form_group(html, self.get_form_group_class())

    def render(self):
        # See if we're not excluded
        if self.field.name in self.exclude.replace(' ', '').split(','):
            return ''
        # Hidden input requires no special treatment
        if isinstance(self.field, AutoField):
            return text_value(getattr(self.object, self.field.name))

        html = text_value(getattr(self.object, self.field.name))

        # Start post render
        html = self.append_to_field(html)
        html = self.wrap_field(html)
        html = self.add_label(html)
        html = self.wrap_label_and_field(html)
        return html