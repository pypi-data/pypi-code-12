# coding=utf-8
import json
from django import template
from django.conf import settings
from django.forms import forms
from django.forms import fields
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.safestring import mark_safe
from scaffold_toolkit.formvalidator.forms.validators import BaseBV, ImageFileValidator
from .utils import convert_datetime_python_to_javascript, get_language

register = template.Library()


def _get_static_url(path):
    from django.contrib.staticfiles.storage import staticfiles_storage

    return staticfiles_storage.url(path)


@register.simple_tag
def formvalidator_javascript(framework='bootstrap', language=None):
    language = get_language() if language is None else language
    language = 'zh_CN' if language == 'zh_HANS' else language
    return '{base}{framework}{language}'.format(
            base='<script src="{url}"></script>'.format(url=_get_static_url('formvalidator/js/formValidation.min.js')),
            framework='<script src="{url}"></script>'.format(
                    url=_get_static_url('formvalidator/js/framework/{}.min.js'.format(framework))),
            language='<script src="{url}"></script>'.format(
                    url=_get_static_url('formvalidator/js/language/{}.js'.format(language)))
    )


@register.simple_tag
def formvalidator_css():
    return '<link href="{url}" rel="stylesheet" />'.format(
            url=_get_static_url('formvalidator/css/formValidation.min.css'))


@register.simple_tag
def formvalidator(selector, form, requirejs=False, *args, **kwargs):
    """

    :param selector:
    :type selector: str
    :param form:
     :type form: django.forms.Form
    :param requirejs:
    :param args:
    :param kwargs:(language,excluded)
    :return:
    """
    if not selector.startswith(u'.') and not selector.startswith('#'):
        selector = '#' + selector
    container = kwargs.pop('err.container', '') or kwargs.pop('container', '')
    icon = kwargs.pop('icon', None)
    excluded = kwargs.pop('excluded', ':disabled, :hidden, :not(:visible)')

    validators = {}
    for field in form:
        validators[field.name] = render_field(field)
    code = (u"$(document).ready(function() {{ \r\n"
            u"      $('{selector}').formValidation({{  \r\n"
            u"          framework: 'bootstrap',  \r\n"
            u"          err:{{container:'{container}'}},  \r\n"
            u"          icon: {icon},  \r\n"
            u"          locale:'{lang}',  \r\n"
            u"          excluded:'{excluded}',  \r\n"
            u"          fields:{fields} \r\n"
            u"      }}) \r\n"
            u'  }});')
    icon = icon.lower() if icon else None
    if icon == 'fa' or icon == 'fontawesome':
        icon_code = (u" { \r\n"
                     u"valid: 'fa fa-check', \r\n"
                     u"invalid: 'fa fa-times', \r\n"
                     u"validating: 'fa fa-refresh' \r\n"
                     u"} \r\n")
    elif icon == 'bootstrap2' or icon == 'zui' or icon == 'buildin':
        icon_code = (u" { \r\n"
                     u"valid: 'icon-ok', \r\n"
                     u"invalid: 'icon-remove', \r\n"
                     u"validating: 'icon-refresh icon-spin' \r\n"
                     u"} \r\n")
    elif icon:
        icon_code = icon
    else:
        icon_code = 'null'
    language = get_language()
    if language == 'zh_HANS':
        language = 'zh_CN'
    vld_code = code.format(selector=selector, container=container, icon=icon_code,
                           excluded=excluded,
                           fields=json.dumps(validators, indent=4), lang=language)
    if requirejs:
        depends = '"jquery","formValidator"'
        language = kwargs.pop('language', get_language())
        depends = '{},"formValidator/language/{}"'.format(depends, language)
        vld_code = u'requirejs([{}],function(){{ {} }})'.format(depends, vld_code)

        return mark_safe("<script>{}</script>".format(get_require_config_code() + vld_code))
    else:
        return mark_safe("<script>{}</script>".format(vld_code))


@register.simple_tag
def formvalidator_fields(form):
    validators = {}
    for field in form:
        validators[field.name] = render_field(field)
    return mark_safe(json.dumps(validators, indent=4))


@register.simple_tag
def formvalidator_requirejs_config(base_url=None, language=None):
    return mark_safe(get_require_config_code(base_url, language))


def get_require_config_code(base_url=None, language=None):
    config = ("""

    if (!require.defined("formValidator")){{
        require.config({{
              paths:{{
              'formValidator':'{bv}/formValidator',
              '_formValidation':'{bv}/js/formValidation.min',
              '_formValidation/framework/bootstrap':'{bv}/js/framework/bootstrap.min',
              'formValidator/language/{lang}':'{bv}/js/language/{lang}',
              }},
              shim:{{
              '_formValidation':['jquery'],
               '_formValidation/framework/bootstrap':['_formValidation'],
              'formValidator':['_formValidation','_formValidation/framework/bootstrap'],
              'formValidator/language/{lang}':['formValidator']
              }}
        }});
    }}
    """)
    if base_url is None:
        bv = getattr(settings, 'FORM_VALIDATOR_PREFIX', '')
        if not bv:
            bv = _get_static_url('formvalidator')
    else:
        bv = base_url
    if bv.endswith("/"):
        bv = bv[:-1]
    language = language if language else get_language()

    return config.format(bv=bv, lang=language)


def render_field(field):
    """
    渲染字段验证代码
    :param field:
     :type field: django.forms.Field
    :return:
    """
    field = field.field if isinstance(field, forms.BoundField) else field
    validators = {}

    def no_compare_validator():
        return not ('lessThan' in validators or 'greaterThan' in validators or 'between' in validators)

    if field.required:
        validators['notEmpty'] = {}
    validator_codes = [item.code for item in field.validators]
    for v in field.validators:
        if isinstance(v, MinLengthValidator):
            vc = validators.get('stringLength', {})
            vc['min'] = field.min_length
            validators.update({'stringLength': vc})
        elif isinstance(v, MaxLengthValidator):
            vc = validators.get('stringLength', {})
            vc['max'] = field.max_length
            validators.update({'stringLength': vc})
        elif isinstance(v, (MinValueValidator, MaxValueValidator)):
            if 'min_value' in validator_codes and 'max_value' in validator_codes:
                vc = validators.get('between', {})
                if v.code == 'min_value':
                    vc['min'] = field.min_value
                else:
                    vc['max'] = field.max_value
                validators.update({'between': vc})
            elif v.code == 'min_value':
                validators['greaterThan'] = {'value': field.min_value}
            elif v.code == 'max_value':
                validators['lessThan'] = {'value': field.max_value}
        elif isinstance(v, BaseBV):
            validators.update(v.get_validator_code())

    if isinstance(field, (fields.DecimalField, fields.FloatField)) and no_compare_validator():
        validators['numeric'] = {}
    elif isinstance(field, fields.IntegerField) and no_compare_validator():
        validators['integer'] = {}
    elif isinstance(field, (fields.DateField, fields.DateTimeField)):
        formats = field.input_formats
        if formats:
            validators['date'] = {'format': convert_datetime_python_to_javascript(formats[0])}
    elif isinstance(field, fields.TimeField):
        validators['regexp'] = {'regexp': '^((([0-1]?[0-9])|([2][0-3])):)(([0-5][0-9]):)([0-5][0-9])$',
                                }
    elif isinstance(field, fields.URLField):
        validators['uri'] = {}
    elif isinstance(field, fields.EmailField):
        validators['emailAddress'] = {}
    elif isinstance(field, fields.ImageField):
        if 'file' not in validators:
            validators.update(ImageFileValidator().get_validator_code())
    return {'validators': validators}
