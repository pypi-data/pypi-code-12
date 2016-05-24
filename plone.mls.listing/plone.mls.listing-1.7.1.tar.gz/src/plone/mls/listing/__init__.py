# -*- coding: utf-8 -*-
"""Plone support for MLS Listings."""

PRODUCT_NAME = 'plone.mls.listing'


class AnnotationStorage(dict):
    """Custom annotation dict for MLS configurations."""

    context = None
