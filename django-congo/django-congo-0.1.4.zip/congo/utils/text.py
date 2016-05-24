# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.utils.exceptions import EmptyContentError, get_exception_description
from django.template.base import Template
from django.template.context import Context
from django.utils import translation
from django.utils.encoding import force_text
from unidecode import unidecode
import re

RE_SPACE = re.compile(r"[\s]+", re.UNICODE)
RE_NON_WORD = re.compile(r"[^ \w\-']", re.UNICODE)

def strip_spaces(value):
    return re.sub(r'>\s+<', '> <', force_text(value))

def strip_comments(value):
    return re.sub(r'<!--[^>]*-->', '', force_text(value))

def strip_emptylines(value):
    return re.sub(r'\n\s*\n', '\n', force_text(value))

def strip_lines(value):
    return re.sub(r'\r*\n', ' ', force_text(value))

def strip_special_chars(text):
    text = force_text(text)
    text = RE_SPACE.sub(" ", text) # Standardize spacing.
    text = RE_NON_WORD.sub("", text) # Remove non-word characters.
    return text

def slugify(value):
    value = unidecode(value)
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def render_content(content, context_dict = {}, context = None, language = None, allow_empty_content = True):
    try:
        template = Template("{% load nested i18n %}" + content.replace(u'\xa0', u' '))

        if not context:
            context = Context()
        context.update(context_dict)

        if language and language != settings.LANGUAGE_CODE:
            translation.activate(language)

        content = template.render(context)

        if language and language != settings.LANGUAGE_CODE:
            translation.deactivate()

        return content
    except EmptyContentError as e:
        if allow_empty_content:
            return ""
        raise # re-raise EmptyContentError
    except Exception as e:
        return get_exception_description(e) if settings.DEBUG else content
