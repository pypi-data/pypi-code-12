# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.utils.text import strip_special_chars
from django.db.models import Q
from django.db.utils import IntegrityError
from django.utils.encoding import force_text
from django.utils.translation import get_language
from watson.registration import SearchEngine, _bulk_save_search_entries
import datetime
import re

site_search_engine = SearchEngine("site_%s" % settings.SITE_ID)
search_languages = [language['code'] for language in settings.PARLER_LANGUAGES[None]]
_language_search_engine = dict([(language, SearchEngine(language)) for language in search_languages])

def get_language_search_engine(language = None):
    if language is None:
        language = get_language()
    if language not in search_languages:
        language = search_languages[0]
    return _language_search_engine[language]

def escape_mysql_query(search_text, default_operator = "+"):
    words = []

    for word in search_text.split():
        if word[0] in "+-":
            operator = word[0]
            word = word[1:]
        else:
            operator = default_operator
        word = strip_special_chars(word)
        if len(word) < 3 and operator:
            operator = ""
        words.append("%s%s*" % (operator, word))

    return " ".join(words)

def rebuild_index_for_model(model, search_engine):
    def iter_search_entries():
        for obj in model._default_manager.all().iterator():
            for search_entry in search_engine._update_obj_index_iter(obj):
                yield search_entry
    _bulk_save_search_entries(iter_search_entries())
