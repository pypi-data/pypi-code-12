# -*- coding: utf-8 -*-
from persistent.mapping import PersistentMapping
import logging

from zope.component import getUtilitiesFor

from Products.CMFPlone.utils import base_hasattr
from plone.dexterity.interfaces import IDexterityFTI

from ..utils import get_localrole_fields

logger = logging.getLogger('dexterity.localroles: upgrade. ')


def v2(context):
    for (name, fti) in getUtilitiesFor(IDexterityFTI):
        for (fname, field) in get_localrole_fields(fti):
            if not base_hasattr(fti, fname):
                continue
            logger.info("FTI '%s' => Copying old field config '%s': '%s'" % (name, fname, getattr(fti, fname)))
            if not base_hasattr(fti, 'localroles'):
                setattr(fti, 'localroles', PersistentMapping())
            fti.localroles[fname] = {}
            for state_key, state_dic in getattr(fti, fname).items():
                fti.localroles[fname][state_key] = {}
                for principal, roles in state_dic.items():
                    fti.localroles[fname][state_key][principal] = {'roles': roles}
            delattr(fti, fname)
