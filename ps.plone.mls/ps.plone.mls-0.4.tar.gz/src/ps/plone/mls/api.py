# -*- coding: utf-8 -*-
"""MLS integration api."""

# python imports
from mls.apiclient import (
    api,
    exceptions,
    resources,
)

# zope imports
from plone import api as plone_api
from plone.mls.core.api import get_settings
from plone.mls.listing.api import get_agency_info
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest

# local imports
from ps.plone.mls import (
    _,
    utils,
)

MIN_MAX_FIELDS = [
    'baths',
    'beds',
    'lot_size',
    'interior_area',
]


def _remove_omitted(params, omit):
    """Removed omitted keys from the params dict."""
    if omit is not None and isinstance(omit, (list, tuple)):
        for item in omit:
            try:
                del params[item]
            except KeyError:
                continue


def prepare_search_params(params, context=None, omit=None):
    """Prepare search params."""
    settings = get_settings(context=context)
    result = {}

    _remove_omitted(params, omit)

    for item in params:
        if item in MIN_MAX_FIELDS:
            min_max = params[item]
            if isinstance(min_max, (list, tuple, )):
                if len(min_max) > 0 and min_max[0] != '--MINVALUE--':
                    result[item + '_min'] = min_max[0]
                if len(min_max) > 1 and min_max[1] != '--MAXVALUE--':
                    result[item + '_max'] = min_max[1]
                continue

        # Convert lists and tuples to comma separated lists.
        if isinstance(params[item], (list, tuple, )):
            if len(params.get(item, ())) > 0:
                params[item] = ','.join(params[item])
            else:
                params[item] = None

        # Remove all None-Type values.
        if params[item] is not None:
            value = params[item]
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            result[item] = value

    agency_developments = result.pop('agency_developments', False)
    if agency_developments is True:
        result['agency_developments'] = settings.get('agency_id', None)

    return result


def get_api(context=None, lang=None):
    """Get the API Client based on the local configuration."""
    settings = get_settings(context=context)
    base_url = settings.get('mls_site', None)
    api_key = settings.get('mls_key', None)
    debug = plone_api.env.debug_mode
    mls = api.API(base_url, api_key=api_key, lang=lang, debug=debug)
    return mls


def get_development(item_id=None, context=None, request=None, lang=None):
    """Get a single development."""
    mlsapi = get_api(context=context, lang=lang)
    try:
        item = Development.get(mlsapi, item_id)
    except exceptions.ServerError:
        if not plone_api.user.is_anonymous():
            message = _(
                u'An error occured trying to connect to the '
                u'configured MLS. Please check your settings or try '
                u'again later.'
            )
            plone_api.portal.show_message(
                message=message,
                request=request,
                type='warning',
            )
    except exceptions.ResourceNotFound:
        message = _(
            u'The requested development was not found.'
        )
        plone_api.portal.show_message(
            message=message,
            request=request,
            type='info',
        )
    except exceptions.ConnectionError:
        pass
    else:
        return item


class Field(object):
    """Wraps the api data into a field structure."""

    def __init__(self, name, value, resource, title=None):
        self.name = name
        self.value = value
        self.title = title

        if self.title is not None:
            return

        # Try to get the correct label for the field.
        titles = resource.field_titles().get('response', {})

        try:
            self.title = titles['fields'][name]
        except (KeyError, TypeError):
            pass
        else:
            return

        group_fields = titles.get('group_fields', [])
        for group in group_fields:
            try:
                self.title = group_fields[group][name]
            except (KeyError, TypeError):
                continue
            else:
                break
        if self.title is None:
            self.title = name


class CacheMixin(object):
    """Extend API resources to handle some caching."""
    _field_titles = None

    def _get_field_titles(self):
        """Get the translated field titles from the API endpoint."""
        return self.__class__.get_field_titles(self._api)

    def field_titles(self):
        """Get the translated field titles for that resource."""
        if self._field_titles is not None:
            return self._field_titles

        request = getRequest()
        key = 'cache-{0}-{1}-{2}'.format(
            self.__class__.__name__,
            self._api.base_url,
            self._api.lang,
        )
        cache = IAnnotations(request)
        data = cache.get(key, None)
        if not data:
            try:
                data = self._get_field_titles()
            except exceptions.ResourceNotFound:
                data = {}
            else:
                cache[key] = data
                self._field_titles = data
        else:
            self._field_titles = data
        return data

    def __getattr__(self, name):
        """Returns a data attribute or raises AttributeError.

        This version wraps the return value into a Field class for better
        access in Plone.
        """
        try:
            value = self._data[name]
        except KeyError:
            return object.__getattribute__(self, name)
        else:
            if value is not None:
                return Field(name, value, self)


class Agency(CacheMixin, resources.Agency):
    """'Agency' entity resource class with caching support."""

    def override(self, context=None):
        """Override the agency information with local settings."""
        settings = get_agency_info(context=context)
        if settings is None:
            return

        mls_settings = get_settings(context=context)
        agency_id = mls_settings.get('agency_id', None)

        if self._data.get('id', None) == agency_id:
            if settings and settings.get('force', False) is True:
                pass
            else:
                return

        mapping = {
            'agency_address': 'address',
            'agency_description': 'description',
            'agency_email': 'email',
            'agency_email_alternative': 'email_alternative',
            'agency_geo_location': 'geo_location',
            'agency_logo_url': 'logo',
            'agency_name': 'title',
            'agency_office_fax': 'office_fax',
            'agency_office_phone': 'office_phone',
            'agency_office_phone_alternative': 'office_phone_alternative',
            'agency_website': 'website',
        }

        utils.merge_local_contact_info(
            settings=settings,
            mapping=mapping,
            data=self._data,
        )


class Agent(CacheMixin, resources.Agent):
    """'Agent' entity resource class with caching support."""

    def override(self, context=None):
        """Override the agent information with local settings."""
        settings = get_agency_info(context=context)
        if settings is None:
            return

        mls_settings = get_settings(context=context)
        agency_id = mls_settings.get('agency_id', None)

        if self._data.get('id', None) == agency_id:
            if settings and settings.get('force', False) is True:
                pass
            else:
                return

        mapping = {
            'agent_avatar_url': 'avatar',
            'agent_cell_phone': 'cell_phone',
            'agent_email': 'email',
            'agent_fax': 'fax',
            'agent_name': 'name',
            'agent_office_phone': 'office_phone',
            'agent_title': 'user_title',
        }

        utils.merge_local_contact_info(
            settings=settings,
            mapping=mapping,
            data=self._data,
        )


class Development(CacheMixin, resources.Development):
    """'Development Project' entity resource class with caching support."""

    def __init__(self, api, data):
        super(Development, self).__init__(api, data)
        self.__class_agency__ = Agency
        self.__class_agent__ = Agent
        self.__class_group__ = PropertyGroup
        self.__class_phase__ = DevelopmentPhase


class DevelopmentPhase(CacheMixin, resources.DevelopmentPhase):
    """'Development Phase' entity resource class with caching support."""


class Listing(CacheMixin, resources.Listing):
    """'Listing' entity resource class with caching support."""


class PropertyGroup(CacheMixin, resources.PropertyGroup):
    """'Property Group' entity resource class with caching support."""
