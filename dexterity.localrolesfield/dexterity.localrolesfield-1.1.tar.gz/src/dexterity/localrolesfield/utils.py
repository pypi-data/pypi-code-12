# -*- coding: utf-8 -*-
"""Utils."""
from zope.component import getUtility

from plone.behavior.interfaces import IBehavior
# from plone.memoize.ram import cache
from dexterity.localrolesfield.interfaces import IBaseLocalRoleField


def cache_key(fun, fti):
    return fti


# @cache(cache_key)  a test with profilehooks.timecall give 0.000s for this method with ten fields and some behaviors
def get_localrole_fields(fti):
    """Get all local role(s) fields for given fti.

    Lookup local role(s) fields on content from its schema and its behaviors.
    Return field name and field object for each found field.
    """
    fti_schema = fti.lookupSchema()
    fields = [(n, f) for n, f in fti_schema.namesAndDescriptions(all=True)
              if IBaseLocalRoleField.providedBy(f)]

    # also lookup behaviors
    for behavior_id in fti.behaviors:
        behavior = getUtility(IBehavior, behavior_id).interface
        fields.extend(
            [(n, f) for n, f in behavior.namesAndDescriptions(all=True)
             if IBaseLocalRoleField.providedBy(f)])

    return fields
