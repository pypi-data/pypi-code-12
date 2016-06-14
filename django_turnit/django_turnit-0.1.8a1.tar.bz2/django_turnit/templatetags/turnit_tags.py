# -*- coding: utf-8 -*-
"""
Template tags for :mod:`django_turnit` application

:creationdate: 07/03/16 09:27
:moduleauthor: François GUÉRIN <frague59@gmail.com>
:modulename: templatetags.turnit_tags

"""
import os
import uuid
import logging
from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

from django_turnit import models

register = template.Library()

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.templatetags.turnit_tags')


def get_render_context(context, pdf_file, width=None):
    """
    Updates the context before rendering PDFFile

    :param context: Template context
    :param pdf_file: PDFFile to render
    :param width: Total width of widget
    :returns: Updated context
    """
    guid = uuid.uuid4().hex
    related_file_id = os.path.relpath(pdf_file.path, settings.MEDIA_ROOT)
    settings.DEBUG and logger.debug(u'get_render_context() related_file_id = %s', related_file_id)
    try:
        page_list = models.PDFFilePage.objects.filter(related_pdf_file=related_file_id)
    except ObjectDoesNotExist as e:
        logger.warning(u'get_render_context() Unable to get thumbnails for file <%s>: %s', related_file_id, e)
        raise
    render_context = {'guid': guid,
                      'page_list': list(page_list)}
    if width:
        width = int(width)
        height = width * 2 // 3
        render_context.update({'width': width})
        render_context.update({'height': height})

    if 'object' in context:
        render_context.update({'title': context['object'].title})

    return render_context


@register.inclusion_tag(file_name='django_turnit/snippets/turnit.html', name='turnit', takes_context=True)
def turnit(context, pdf_file, width=480):
    """
    Displays a `turn.js` widget

    :param context: Template context
    :param pdf_file: PDFFile to render
    :param width: Total width of widget
    :returns: rendered widget
    """
    settings.DEBUG and logger.debug(u'turnit() pdf_file = %s', pdf_file.url)
    render_context = get_render_context(context=context, pdf_file=pdf_file, width=width)
    settings.DEBUG and logger.debug(u'turnit() render_context = %s', render_context)
    return render_context


@register.inclusion_tag(file_name='django_turnit/snippets/turnit_modal.html', name='turnit_modal', takes_context=True)
def turnit_modal(context, pdf_file):
    """
    Displays a `turn.js` widget in a modal html window

    :param context: HTTP context
    :param pdf_file: file to render
    :returns: rendered widget
    """
    settings.DEBUG and logger.debug(u'turnit_modal() pdf_file = %s', pdf_file.url)
    render_context = get_render_context(context, pdf_file, width=800)
    if isinstance(render_context['page_list'], (list, tuple)) and len(render_context['page_list']) > 0:
        render_context.update({'first_page': render_context['page_list'][0]})
    settings.DEBUG and logger.debug(u'turnit_modal() render_context = %s', render_context)
    return render_context


@register.filter
def divide(val, divider):
    """
    Integer divides a value by a divider

    :param val: value to divide
    :param divider: divider value
    :returns: divided value

    >>> divide(10, 2)
    '5'
    >>> divide(15, 2)
    '7'
    >>> divide(15, 0)  # divides a value by 0
    ''
    """
    # noinspection PyBroadException
    try:
        return mark_safe(str(int(val) // int(divider)))
    except Exception:
        return mark_safe('')

