"""
views for ip registry (iprir) project
"""

import json

from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse, Http404

from .models import Registry, TLD, InetNum
from .helpers import ip_info


def index(request):

    """
    returns remote ip registry info in a JSON string
    """

    context = ip_info(request)

    output = json.dumps(context, sort_keys=True)
    return HttpResponse(str(output))


def json_by_ip(request, address):

    """
    returns any ip registry info in a JSON string
    """

    context = ip_info(request, address)

    output = json.dumps(context, sort_keys=True)
    return HttpResponse(str(output))


def dict_by_ip(request, address):

    """
    Sample returns any ip registry info in a dict
    """

    return HttpResponse(str(ip_info(request, address)))


def registry_by_id(request, registry_id):

    """
    returns registry entries for specific Regional Internet Registry by id
    """

    try:
        registry = Registry.objects.get(pk=registry_id)
    except Registry.DoesNotExist:
        raise Http404

    return render(request, 'iprir/registry.html', {'Registry': registry})


@require_http_methods(["GET"])
def registry_by_desc(request, registry_desc):

    """
    returns registry entries for specific Regional Internet Registry by desc
    """

    try:
        registry = Registry.objects.get(registryDesc=registry_desc)
    except Registry.DoesNotExist:
        raise Http404

    return render(request, 'iprir/registry.html', {'Registry': registry})


@require_http_methods(["GET"])
def tld_by_domain(request, tld_domain):

    """
    returns registry entries for specific top level domain
    """

    try:
        tld = TLD.objects.get(domain__iexact=tld_domain)
    except TLD.DoesNotExist:
        raise Http404

    return render(request, 'iprir/tld.html', {'tld': tld})
