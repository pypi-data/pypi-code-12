# -*- coding: utf-8 -*-

# zope imports
from zope.interface import Interface


class IListingTraversable(Interface):
    """Marker interface for traversable listings."""


class IDevelopmentTraversable(Interface):
    """Marker interface for traversable listings."""


class IBaseDevelopmentItems(IDevelopmentTraversable):
    """Marker interface for all development 'collection' items."""


class IDevelopmentCollection(IBaseDevelopmentItems):
    """Marker interface for DevelopmentCollection viewlet."""


class IDevelopmentDetails(Interface):
    """Marker interface for DevelopmentDetails view."""


class IPossibleDevelopmentCollection(Interface):
    """Marker interface for possible DevelopmentCollection viewlet."""
