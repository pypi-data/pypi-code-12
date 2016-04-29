# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

from .brood_url_handler import BroodURLHandler
from .model_registry import ModelRegistry
from .url_templates import URLS


class BroodClient(object):
    """``BroodClient`` is the top level entry point into the ``hatcher``
    API.

    """

    def __init__(self, url_handler, api_version=0):
        self._url_handler = url_handler
        self._model_registry = ModelRegistry(api_version=api_version)

    @property
    def _api_version(self):
        return self._model_registry.api_version

    @classmethod
    def from_url(cls, url, auth=None, verify_ssl=True, api_version=0):
        """Create a ``BroodClient`` from a Brood URL and authentication
        information.

        """
        url_handler = BroodURLHandler.from_auth(
            url, auth=auth, verify_ssl=verify_ssl)
        return cls(url_handler=url_handler, api_version=api_version)

    @classmethod
    def from_session(cls, url, session, api_version=0):
        """Create a ``BroodClient`` from a Brood URL and pre-configured
        ``requests.Session`` instance.

        """
        url_handler = BroodURLHandler.from_session(url, session)
        return cls(url_handler=url_handler, api_version=api_version)

    def create_organization(self, name, description):
        """Create a new organization called ``name`` with the description
        ``description``.

        Parameters
        ----------
        name : str
            The name of the organization.
        description : str
            The description of the organization.

        Returns :class:`~hatcher.core.organization.Organization`

        """
        data = {
            'name': name,
            'description': description,
        }
        path = URLS.v0.admin.organizations.format()
        self._url_handler.post(path, data)
        return self.organization(name)

    def organization(self, name):
        """Get an existing organization.

        Parameters
        ----------
        name : str
            The name of the organization.

        Returns :class:`~hatcher.core.organization.Organization`

        """
        return self._model_registry.Organization(
            name, url_handler=self._url_handler,
            model_registry=self._model_registry)

    def list_organizations(self):
        """List all organizations in the brood server.

        """
        path = URLS.v0.admin.organizations.format()
        data = self._url_handler.get_json(path)
        return list(sorted(data['organizations']))

    def create_api_token(self, name):
        """Create a new API token for the current user.

        Parameters
        ----------
        name : str
            The name for the new token.

        Returns
        -------
        token : dict
            Dict containing the token and its name.

        """
        path = URLS.v0.tokens.api.format()
        data = {'name': name}
        response = self._url_handler.post(path, data)
        return response.json()

    def delete_api_token(self, name):
        """Delete the user's named API token.

        Parameters
        ----------
        name : str
            The name of the token to delete.

        """
        path = URLS.v0.tokens.api.delete.format(name=name)
        self._url_handler.delete(path)

    def list_api_tokens(self):
        """List the metadata of user's API tokens.

        .. note::
            This does not list the actual token that can be used for
            authentication, just the metadata ``name``, ``created`` and
            ``last_used``.

        Returns
        -------
        tokens : list
            List of metadata for all of the user's active tokens.

        """
        path = URLS.v0.tokens.api.format()
        tokens = self._url_handler.get_json(path)
        return tokens['tokens']

    def list_platforms(self):
        """List all platforms supported by the Brood server.

        Returns
        -------
        platforms : list
            List of platform names.

        """
        path = URLS.v0.metadata.platforms.format()
        platforms = self._url_handler.get_json(path)
        return platforms['platforms']

    def list_python_tags(self, list_all=False):
        """List PEP425 Python Tags supported by the Brood server.

        Parameters
        ----------
        list_all : bool
            If ``False`` (default), will only list the tags that
            correspond to an actual Python implementation and version.
            If ``True``, list all possible tags.

        Returns
        -------
        tags : list
            List of Python tags.

        """
        if list_all:
            path = URLS.v0.metadata.python_tags.all.format()
        else:
            path = URLS.v0.metadata.python_tags.format()
        python_tags = self._url_handler.get_json(path)
        return python_tags['python_tags']

    def list_available_repositories(self, include_indexable=False):
        """List the repositories to which the user has at least read access.
        When the optional ``include_indexable`` flag is ``True``, the
        list will additionally include repositories to which the user
        only has indexable access.

        Parameters
        ----------
        include_indexable : bool
            When ``True``, the list will additionally include
            repositories to which the user only has indexable
            access. (Default: ``False``)

        """
        path = URLS.v0.user.repositories.format()
        repositories = self._url_handler.get_json(
            path, include_indexable=include_indexable)
        return repositories['repositories']
