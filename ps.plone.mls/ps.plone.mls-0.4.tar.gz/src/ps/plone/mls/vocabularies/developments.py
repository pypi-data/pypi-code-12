# -*- coding: utf-8 -*-
"""Vocabularies for development projects."""

# zope imports
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# local imports
from ps.plone.mls import _


@implementer(IVocabularyFactory)
class SortOptionsVocabulary(object):

    def __call__(self, context):
        items = []
        items.append(SimpleTerm('created', _(u'Creation Date')))
        items.append(SimpleTerm('sortable_title', _(u'Title')))
        return SimpleVocabulary(items)

SortOptionsVocabularyFactory = SortOptionsVocabulary()
