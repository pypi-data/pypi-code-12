""" This module provides the views for the web pages. """

# pylint: disable=no-self-use

from urlparse import urljoin

from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout as auth_logout
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.list import ListView

from doi_site import settings
from doi_site.exception import ExternalError
from doi_site.settings import DATACITE_HANDLER, DATACITE_TEST_URL, \
    DATACITE_URL, DOI_PREFIX, ORGANISATION_NAME, ORGANISATION_DOI_EMAIL
from mds.http.get import get as _get
from mds.models import GroupProfile


# pylint: disable=too-many-ancestors
class DoiList(ListView):
    """
    Display all the DOIs for this organisation.

    """
    paginate_by = 25
    template_name = 'doi_site/dois.html'
    context_object_name = 'dois'

    def dispatch(self, *args, **kwargs):
        return super(DoiList, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            return super(DoiList, self).get(request, *args, **kwargs)
        except ExternalError as ex:
            context = {'message': ex.message}
            context['is_testing'] = _is_test_url()
            return render(request, 'doi_site/error.html', context)

    def get_queryset(self):
        """
        Get the list of DOIs.

        """
        url = urljoin(DATACITE_URL, "doi")
        response = _get('GET', url, {})
        if response.status_code != 200:
            raise ExternalError(response.content)
        dois = []
        for line in response:
            if line != '':
                dois.append(line.strip().decode('ISO-8859-1'))
        return dois

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DoiList, self).get_context_data(**kwargs)
        context['is_testing'] = _is_test_url()
        context['handler'] = DATACITE_HANDLER
        context['doi_prefix'] = DOI_PREFIX
        context['search'] = DATACITE_URL
        return context


class HomeView(View):
    """
    Display the home page.

    """

    def get(self, request):
        """
        Get the home page.

        """
        context = {'organisation_name' : ORGANISATION_NAME}
        context['organisation_email'] = ORGANISATION_DOI_EMAIL
        context['is_testing'] = _is_test_url()
        return render(request, 'doi_site/index.html', context)


class Notes(View):
    """
    Display the notes page.

    """

    def dispatch(self, *args, **kwargs):
        return super(Notes, self).dispatch(*args, **kwargs)

    def get(self, request):
        """
        Get the notes page.

        """
        context = {'organisation_name' : ORGANISATION_NAME}
        context['is_testing'] = _is_test_url()
        context['roles'] = getattr(settings, 'ROLES_URL', '')
        context['notes'] = getattr(settings, 'NOTES_URL', '')
        return render(request, 'doi_site/notes.html', context)


# pylint: disable=too-many-ancestors
class Domains(ListView):
    """
    Display the list of DOI domains.

    """

    model = GroupProfile
    context_object_name = 'group_profiles'
    template_name = 'doi_site/domains.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Domains, self).get_context_data(**kwargs)
        context['doi_prefix'] = DOI_PREFIX + '/'
        context['is_testing'] = _is_test_url()
        return context


def login(request):
    """
    Display the login page.

    """
    context = {'is_testing' : _is_test_url()}
    context['organisation_name'] = ORGANISATION_NAME
    return auth_login(request, extra_context=context)


def logout(request):
    """
    Respond to a logout request.

    """
    context = {'is_testing' : _is_test_url()}
    return auth_logout(request, extra_context=context)


def _is_test_url():
    """
    Are we using the DataCite test service?

    Return:
        a boolean, True if we are using the DataCite test service

    """
    if DATACITE_URL == DATACITE_TEST_URL:
        return True
    return False

