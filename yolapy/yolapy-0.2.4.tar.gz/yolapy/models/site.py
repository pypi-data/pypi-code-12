from demands.pagination import PaginatedAPIIterator
from six import iteritems

from yolapy.constants import SiteStates
from yolapy.services import Yola


class Site(object):
    """Represents a Site resource on the Yola API."""

    def __init__(self, **kwargs):
        self._fields = kwargs
        for key, val in iteritems(kwargs):
            setattr(self, key, val)
        self.publishing_data = kwargs.get('publishing_data') or {}

    def __eq__(self, other):
        return self._fields == other._fields

    @classmethod
    def get(cls, site_id):
        """Get a site from the Yola API."""
        site_attributes = Yola().get_site(site_id)
        return cls(**site_attributes)

    @classmethod
    def list(cls, **filters):
        """Get a list of sites from the Yola API."""
        sites = PaginatedAPIIterator(Yola().list_sites, kwargs=filters)
        return [Site(**s) for s in sites]

    @property
    def is_published(self):
        return self.publishing_data.get('state') == SiteStates.PUBLISHED
