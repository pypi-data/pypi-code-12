# -*- coding: utf-8 -*-
"""Provides vendor_domain object."""

from __future__ import absolute_import
from ..entity import Entity


class VendorDomain(Entity):
    """Provides vendor domain entity."""
    collection = 'vendor_domains'
    resource = 'vendor_domain'
    _relations = {
        'pixels',
        'vendor',
        'vendor_pixel_domains',
    }
    _pull = {
        'allow_subdomain_match': Entity._int_to_bool,
        'created_on': Entity._strpt,
        'domain': None,
        'id': int,
        'updated_on': Entity._strpt,
        'vendor_id': int,
        'version': int,
    }
    _push = _pull.copy()
    _push.update({
        'allow_subdomain_match': int,
    })

    def __init__(self, session, properties=None, **kwargs):
        super(VendorDomain, self).__init__(session, properties, **kwargs)
