# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from math import floor

from django import template
from django.template.loader import get_template

from ..zui import (
    css_url, javascript_url, jquery_url, theme_url, get_zui_setting
)
from ..utils import render_link_tag
from ..forms import (
    render_button, render_field, render_field_and_label, render_form,
    render_form_group, render_formset,
    render_label, render_form_errors, render_formset_errors
)
from ..components import render_icon, render_alert
from ..utils import handle_var, parse_token_contents
from ..text import force_text

register = template.Library()


@register.filter
def zui_setting(value):
    """
    A simple way to read zui settings in a template.
    Please consider this filter private for now, do not use it in your own
    templates.
    """
    return get_zui_setting(value)


@register.simple_tag
def zui_jquery_url():
    """
    **Tag name**::

        zui_jquery_url

    Return the full url to jQuery file to use

    Default value: ``//code.jquery.com/jquery.min.js``

    This value is configurable, see Settings section

    **usage**::

        {% zui_jquery_url %}

    **example**::

        {% zui_jquery_url %}
    """
    return jquery_url()


@register.simple_tag
def zui_javascript_url():
    """
    Return the full url to the zui JavaScript library

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        zui_javascript_url

    **usage**::

        {% zui_javascript_url %}

    **example**::

        {% zui_javascript_url %}
    """
    return javascript_url()


@register.simple_tag
def zui_css_url():
    """
    Return the full url to the zui CSS library

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        zui_css_url

    **usage**::

        {% zui_css_url %}

    **example**::

        {% zui_css_url %}
    """
    return css_url()


@register.simple_tag
def zui_theme_url():
    """
    Return the full url to a zui theme CSS library

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        zui_css_url

    **usage**::

        {% zui_css_url %}

    **example**::

        {% zui_css_url %}
    """
    return theme_url()


@register.simple_tag
def zui_css():
    """
    Return HTML for zui CSS
    Adjust url in settings. If no url is returned, we don't want this statement
    to return any HTML.
    This is intended behavior.

    Default value: ``FIXTHIS``

    This value is configurable, see Settings section

    **Tag name**::

        zui_css

    **usage**::

        {% zui_css %}

    **example**::

        {% zui_css %}
    """
    urls = [url for url in [zui_css_url(), zui_theme_url()] if url]
    return ''.join([render_link_tag(url) for url in urls])


@register.simple_tag
def zui_javascript(jquery=None):
    """
    Return HTML for zui JavaScript.

    Adjust url in settings. If no url is returned, we don't want this
    statement to return any HTML.
    This is intended behavior.

    Default value: ``None``

    This value is configurable, see Settings section

    **Tag name**::

        zui_javascript

    **Parameters**:

        :jquery: Truthy to include jQuery as well as zui

    **usage**::

        {% zui_javascript %}

    **example**::

        {% zui_javascript jquery=1 %}
    """

    javascript = ''
    # See if we have to include jQuery
    if jquery is None:
        jquery = get_zui_setting('include_jquery', False)
    # NOTE: No async on scripts, not mature enough. See issue #52 and #56
    if jquery:
        url = zui_jquery_url()
        if url:
            javascript += '<script src="{url}"></script>'.format(url=url)
    url = zui_javascript_url()
    if url:
        javascript += '<script src="{url}"></script>'.format(url=url)
    return javascript


@register.simple_tag
def zui_formset(*args, **kwargs):
    """
    Render a formset


    **Tag name**::

        zui_formset

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_formset formset %}

    **example**::

        {% zui_formset formset layout='horizontal' %}

    """
    return render_formset(*args, **kwargs)


@register.simple_tag
def zui_formset_errors(*args, **kwargs):
    """
    Render formset errors

    **Tag name**::

        zui_formset_errors

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_formset_errors formset %}

    **example**::

        {% zui_formset_errors formset layout='inline' %}
    """
    return render_formset_errors(*args, **kwargs)


@register.simple_tag
def zui_form(*args, **kwargs):
    """
    Render a form

    **Tag name**::

        zui_form

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_form form %}

    **example**::

        {% zui_form form layout='inline' %}
    """
    return render_form(*args, **kwargs)


@register.simple_tag
def zui_form_errors(*args, **kwargs):
    """
    Render form errors

    **Tag name**::

        zui_form_errors

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_form_errors form %}

    **example**::

        {% zui_form_errors form layout='inline' %}
    """
    return render_form_errors(*args, **kwargs)


@register.simple_tag
def zui_field(*args, **kwargs):
    """
    Render a field

    **Tag name**::

        zui_field

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_field form_field %}

    **example**::

        {% zui_field form_field %}
    """
    return render_field(*args, **kwargs)


@register.simple_tag()
def zui_label(*args, **kwargs):
    """
    Render a label

    **Tag name**::

        zui_label

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_label FIXTHIS %}

    **example**::

        {% zui_label FIXTHIS %}
    """
    return render_label(*args, **kwargs)


@register.simple_tag
def zui_button(*args, **kwargs):
    """
    Render a button

    **Tag name**::

        zui_button

    **Parameters**:

        :args:
        :kwargs:

    **usage**::

        {% zui_button FIXTHIS %}

    **example**::

        {% zui_button FIXTHIS %}
    """
    return render_button(*args, **kwargs)


@register.simple_tag
def zui_icon(icon, **kwargs):
    """
    Render an icon

    **Tag name**::

        zui_icon

    **Parameters**:

        :icon: icon name

    **usage**::

        {% zui_icon "icon_name" %}

    **example**::

        {% zui_icon "star" %}

    """
    return render_icon(icon, **kwargs)


@register.simple_tag
def zui_alert(content, alert_type='info', dismissable=True):
    """
    Render an alert

    **Tag name**::

        zui_alert

    **Parameters**:

        :content: HTML content of alert
        :alert_type: one of 'info', 'warning', 'danger' or 'success'
        :dismissable: boolean, is alert dismissable

    **usage**::

        {% zui_alert "my_content" %}

    **example**::

        {% zui_alert "Something went wrong" alert_type='error' %}

    """
    return render_alert(content, alert_type, dismissable)


@register.tag('buttons')
def zui_buttons(parser, token):
    """
    Render buttons for form

    **Tag name**::

        zui_buttons

    **Parameters**:

        :parser:
        :token:

    **usage**::

        {% zui_buttons FIXTHIS %}

    **example**::

        {% zui_buttons FIXTHIS %}
    """
    kwargs = parse_token_contents(parser, token)
    kwargs['nodelist'] = parser.parse(('endbuttons',))
    parser.delete_first_token()
    return ButtonsNode(**kwargs)


class ButtonsNode(template.Node):
    def __init__(self, nodelist, args, kwargs, asvar, **kwargs2):
        self.nodelist = nodelist
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        output_kwargs = {}
        for key in self.kwargs:
            output_kwargs[key] = handle_var(self.kwargs[key], context)
        buttons = []
        submit = output_kwargs.get('submit', None)
        reset = output_kwargs.get('reset', None)
        if submit:
            buttons.append(zui_button(submit, 'submit'))
        if reset:
            buttons.append(zui_button(reset, 'reset'))
        buttons = ' '.join(buttons) + self.nodelist.render(context)
        output_kwargs.update({
            'label': None,
            'field': buttons,
        })
        output = render_form_group(render_field_and_label(**output_kwargs))
        if self.asvar:
            context[self.asvar] = output
            return ''
        else:
            return output


@register.simple_tag(takes_context=True)
def zui_messages(context, *args, **kwargs):
    """
    Show django.contrib.messages Messages in zui alert containers.

    In order to make the alerts dismissable (with the close button),
    we have to set the jquery parameter too when using the
    zui_javascript tag.

    **Tag name**::

        zui_messages

    **Parameters**:

        :context:
        :args:
        :kwargs:

    **usage**::

        {% zui_messages FIXTHIS %}

    **example**::

        {% zui_javascript jquery=1 %}
        {% zui_messages FIXTHIS %}

    """
    return get_template('zui/messages.html').render(context)


@register.inclusion_tag('zui/zui_pagination.html')
def zui_pagination(page, **kwargs):
    """
    Render pagination for a page

    **Tag name**::

        zui_pagination

    **Parameters**:

        :page:
        :parameter_name: Name of paging URL parameter (default: "page")
        :kwargs:

    **usage**::

        {% zui_pagination FIXTHIS %}

    **example**::

        {% zui_pagination FIXTHIS %}
    """

    pagination_kwargs = kwargs.copy()
    pagination_kwargs['page'] = page
    return get_pagination_context(**pagination_kwargs)


def get_pagination_context(page, pages_to_show=11,
                           url=None, size=None, extra=None,
                           parameter_name='page'):
    """
    Generate zui pagination context from a page object
    """
    pages_to_show = int(pages_to_show)
    if pages_to_show < 1:
        raise ValueError("Pagination pages_to_show should be a positive " +
                         "integer, you specified {pages}".format(
                             pages=pages_to_show))
    num_pages = page.paginator.num_pages
    current_page = page.number
    half_page_num = int(floor(pages_to_show / 2)) - 1
    if half_page_num < 0:
        half_page_num = 0
    first_page = current_page - half_page_num
    if first_page <= 1:
        first_page = 1
    if first_page > 1:
        pages_back = first_page - half_page_num
        if pages_back < 1:
            pages_back = 1
    else:
        pages_back = None
    last_page = first_page + pages_to_show - 1
    if pages_back is None:
        last_page += 1
    if last_page > num_pages:
        last_page = num_pages
    if last_page < num_pages:
        pages_forward = last_page + half_page_num
        if pages_forward > num_pages:
            pages_forward = num_pages
    else:
        pages_forward = None
        if first_page > 1:
            first_page -= 1
        if pages_back is not None and pages_back > 1:
            pages_back -= 1
        else:
            pages_back = None
    pages_shown = []
    for i in range(first_page, last_page + 1):
        pages_shown.append(i)
        # Append proper character to url
    if url:
        # Remove existing page GET parameters
        url = force_text(url)
        url = re.sub(r'\?{0}\=[^\&]+'.format(parameter_name), '?', url)
        url = re.sub(r'\&{0}\=[^\&]+'.format(parameter_name), '', url)
        # Append proper separator
        if '?' in url:
            url += '&'
        else:
            url += '?'
            # Append extra string to url
    if extra:
        if not url:
            url = '?'
        url += force_text(extra) + '&'
    if url:
        url = url.replace('?&', '?')
    # Set CSS classes, see http://getzui.com/components/#pagination
    pagination_css_classes = ['paper']
    # if size == 'small':
    #     pagination_css_classes.append('pagination-sm')
    # elif size == 'large':
    #     pagination_css_classes.append('pagination-lg')
    #     # Build context object
    return {
        'zui_pagination_url': url,
        'num_pages': num_pages,
        'current_page': current_page,
        'first_page': first_page,
        'last_page': last_page,
        'pages_shown': pages_shown,
        'pages_back': pages_back,
        'pages_forward': pages_forward,
        'pagination_css_classes': ' '.join(pagination_css_classes),
        'parameter_name': parameter_name,
    }


@register.simple_tag
def zui_static(field_name, field_value, label_css_class='col-md-3', field_css_field='col-md-9'):
    """

    :param field_name:
    :param field_value:
    :param label_css_class:
    :param field_css_field:
    :return:
    """

    tmp = u"""
    <div class="form-group">
    <label class="{label_css_class} control-label">{field_name}</label>
    <div class="{field_css_class}">
      <p class="form-control-static">{field_value}</p>
    </div>
  </div>
    """
    if isinstance(field_value, bool):
        field_value = u'是' if field_value else u'否'
    else:
        field_value = field_value if field_value else u''
    return tmp.format(**{'label_css_class': label_css_class,
                         'field_name': field_name,
                         'field_css_class': field_css_field,
                         'field_value': field_value})
