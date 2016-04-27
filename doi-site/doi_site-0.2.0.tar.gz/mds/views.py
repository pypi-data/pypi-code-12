""" This module provides the views for the ReST API. """

# pylint: disable=no-self-use

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from doi_site.settings import DATACITE_URL
from mds.basic_auth import logged_in_or_basicauth
from mds.http.delete import delete_metadata
from mds.http.get import get as _get
from mds.http.helper import get_accept_header
from mds.http.post import post_doi, post_media, post_metadata
from urlparse import urljoin


class MetadataView(View):
    """
    Handle delete, head and get requests for metadata.

    """
    @method_decorator(csrf_exempt)
    @method_decorator(logged_in_or_basicauth())
    def dispatch(self, *args, **kwargs):
        return super(MetadataView, self).dispatch(*args, **kwargs)

    def delete(self, request):
        """
        This request marks a dataset as 'inactive'. To activate it again, POST
        new metadata or set the isActive-flag in the user interface.

        """
        return delete_metadata(request)

    def get(self, request):
        """
        This request returns the most recent version of metadata associated with
        a given DOI.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))

    def head(self, request):
        """
        Request the most recent version of metadata associated with a given DOI.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))


class MetadataPost(View):
    """
    Handle post requests for metadata.

    """
    @method_decorator(csrf_exempt)
    @method_decorator(logged_in_or_basicauth())
    def dispatch(self, *args, **kwargs):
        return super(MetadataPost, self).dispatch(*args, **kwargs)

    def post(self, request):
        """
        This request stores new version of metadata. The request body must
        contain valid XML.

        """
        return post_metadata(request)


class DoiView(View):
    """
    Handle post requests for DOIs and get and head requests for all DOIs.

    """
    @method_decorator(csrf_exempt)
    @method_decorator(logged_in_or_basicauth())
    def dispatch(self, *args, **kwargs):
        return super(DoiView, self).dispatch(*args, **kwargs)

    def get(self, request):
        """
        This request returns a list of all DOIs for the requesting datacentre.
        There is no guaranteed order.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))

    def head(self, request):
        """
        Request a list of all DOIs for the requesting datacentre.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))

    def post(self, request):
        """
        POST will mint new DOI if specified DOI doesn't exist. This method will
        attempt to update URL if you specify existing DOI. Standard domains and
        quota restrictions check will be performed. A Datacentre's doiQuotaUsed
        will be increased by 1. A new record in Datasets will be created.

        """
        return post_doi(request)


class DoiDetail(View):
    """
    Handle get and head requests for an individual DOIs.

    """

    @method_decorator(logged_in_or_basicauth())
    def dispatch(self, *args, **kwargs):
        return super(DoiDetail, self).dispatch(*args, **kwargs)

    def get(self, request):
        """
        This request returns an URL associated with a given DOI.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))

    def head(self, request):
        """
        Request an URL associated with a given DOI.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))


class MediaView(View):
    """
    Handle head, get and post requests for media.

    """

    @method_decorator(csrf_exempt)
    @method_decorator(logged_in_or_basicauth())
    def dispatch(self, *args, **kwargs):
        return super(MediaView, self).dispatch(*args, **kwargs)

    def get(self, request):
        """
        This request returns list of pairs of media type and URLs associated
        with a given DOI.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))

    def head(self, request):
        """
        Request list of pairs of media type and URLs associated with a given
        DOI.

        """
        url = urljoin(DATACITE_URL, request.get_full_path())
        return _get(request.method, url, get_accept_header(request))

    def post(self, request):
        """
        POST will add/update media type/urls pairs to a DOI. Standard domain
        restrictions check will be performed.

        """
        return post_media(request)

