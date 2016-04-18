# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from future.builtins import int, open

import os
from shuyucms.utils.models import get_model

try:
    from urllib.parse import urljoin, urlparse
except ImportError:
    from urlparse import urljoin, urlparse

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.options import ModelAdmin
from django.contrib.staticfiles import finders
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseServerError,
                         HttpResponseNotFound)
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token
from django.db.models import Q
from shuyucms.conf import settings
from shuyucms.core.forms import get_edit_form
from shuyucms.core.models import Displayable
from shuyucms.utils.cache import add_cache_bypass
from shuyucms.utils.views import is_editable, paginate, render, set_cookie
from shuyucms.utils.urls import next_url
from wlapps.ucenter.models import Project, Organization, UCenter
from wlapps.utils.elasticsearch import elasticsearch
from wlapps.ucenter.views import get_org_model, get_prj_model
from wlapps.ucenter import PRJ_TYPE_ADAPTION_REVERSE, PRJ_TYPE_NAME, ORG_TYPE_ADAPTION_REVERSE, ORG_TYPE_NAME
from shuyucms.utils.cache import cache_installed, _hashed_key, cache_get, cache_set
from django.views.decorators.cache import never_cache


def set_device(request, device=""):
    """
    Sets a device name in a cookie when a user explicitly wants to go
    to the site for a particular device (eg mobile).
    """
    response = redirect(add_cache_bypass(next_url(request) or "/"))
    set_cookie(response, "shuyucms-device", device, 60 * 60 * 24 * 365)
    return response


@staff_member_required
def set_site(request):
    """
    Put the selected site ID into the session - posted to from
    the "Select site" drop-down in the header of the admin. The
    site ID is then used in favour of the current request's
    domain in ``shuyucms.core.managers.CurrentSiteManager``.
    """
    site_id = int(request.GET["site_id"])
    request.session["site_id"] = site_id
    admin_url = reverse("admin:index")
    next = next_url(request) or admin_url
    # Don't redirect to a change view for an object that won't exist
    # on the selected site - go to its list view instead.
    if next.startswith(admin_url):
        parts = next.split("/")
        if len(parts) > 4 and parts[4].isdigit():
            next = "/".join(parts[:4])
    return redirect(next)


def direct_to_template(request, template, extra_context=None, **kwargs):
    """
    Replacement for Django's ``direct_to_template`` that uses
    ``TemplateResponse`` via ``shuyucms.utils.views.render``.
    """
    context = extra_context or {}
    context["params"] = kwargs
    for (key, value) in context.items():
        if callable(value):
            context[key] = value()
    return render(request, template, context)


@staff_member_required
def edit(request):
    """
    Process the inline editing form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_edit_form(obj, request.POST["fields"], data=request.POST,
                         files=request.FILES)
    if not is_editable(obj, request):
        response = _("Permission denied")
    elif form.is_valid():
        form.save()
        model_admin = ModelAdmin(model, admin.site)
        message = model_admin.construct_change_message(request, form, None)
        model_admin.log_change(request, obj, message)
        response = ""
    else:
        response = list(form.errors.values())[0][0]
    return HttpResponse(response)


@never_cache
def search(request, template="search_results.html"):
    """
    按机构、供需和用户来搜索
    """
    # 同一ip搜索频率的限制
    if cache_installed():
        cache_key = "zdsearch" + request.META["REMOTE_ADDR"]
        cv = cache_get(_hashed_key(cache_key))
        if cv:
            if int(cv) < 12:
                cache_set(_hashed_key(cache_key), str(int(cv) + 1), timeout=60)
            else:
                context = {"isprohibited": '1'}
                return render(request, template, context)
        else:
            cache_set(_hashed_key(cache_key), '1', timeout=60)
    query = request.GET.get("q", "")
    query = query.strip()
    if len(query) > 15:
        query = query[:15]
    page = request.GET.get("page", 1)
    per_page = settings.LIST_PER_PAGE
    search_type = request.GET.get("type")
    max_paging_links = settings.MAX_PAGING_LINKS
    tempr = []
    if search_type == 'org':
        tempr = elasticsearch(query, 'org', offset=((int(page) - 1) * 15))
    elif search_type == 'prj':
        tempr = Project.objects.filter(Q(title__istartswith=query)).order_by('-id')
    elif search_type == 'user':
        tempr = elasticsearch(query, 'ucenter', offset=((int(page) - 1) * 15))
    tempr = paginate(tempr, page, per_page, max_paging_links)
    results = []
    if search_type == 'org':
        for item in tempr:
            org_model = get_org_model(ORG_TYPE_ADAPTION_REVERSE[item.orgType])
            s = org_model.objects.get(id=int(item.orgId))
            s.type = ORG_TYPE_NAME[item.orgType]
            results.append(s)
    elif search_type == 'prj':
        for item in tempr:
            the_model = get_prj_model(PRJ_TYPE_ADAPTION_REVERSE[item.prjType])
            ins = the_model.objects.get(id=int(item.prjId))
            ins.type = PRJ_TYPE_NAME[item.prjType]
            if item.prjType == '15':
                ins.title = ins.ucenter_id.title
                ins.description = ins.researchinterest
            results.append(ins)
    elif search_type == 'user':
        results = tempr
        for item in results:
            item.description = "&nbsp;" + item.unit_title + "&nbsp;-&nbsp;" + item.duty

    context = {"query": query, "results": results, "page_results": tempr,
               "search_type": search_type, }
    return render(request, template, context)


@staff_member_required
def static_proxy(request):
    """
    Serves TinyMCE plugins inside the inline popups and the uploadify
    SWF, as these are normally static files, and will break with
    cross-domain JavaScript errors if ``STATIC_URL`` is an external
    host. URL for the file is passed in via querystring in the inline
    popup plugin template, and we then attempt to pull out the relative
    path to the file, so that we can serve it locally via Django.
    """
    normalize = lambda u: ("//" + u.split("://")[-1]) if "://" in u else u
    url = normalize(request.GET["u"])
    host = "//" + request.get_host()
    static_url = normalize(settings.STATIC_URL)
    for prefix in (host, static_url, "/"):
        if url.startswith(prefix):
            url = url.replace(prefix, "", 1)
    response = ""
    content_type = ""
    path = finders.find(url)
    if path:
        if isinstance(path, (list, tuple)):
            path = path[0]
        if url.endswith(".htm"):
            # Inject <base href="{{ STATIC_URL }}"> into TinyMCE
            # plugins, since the path static files in these won't be
            # on the same domain.
            static_url = settings.STATIC_URL + os.path.split(url)[0] + "/"
            if not urlparse(static_url).scheme:
                static_url = urljoin(host, static_url)
            base_tag = "<base href='%s'>" % static_url
            content_type = "text/html"
            with open(path, "r") as f:
                response = f.read().replace("<head>", "<head>" + base_tag)
        else:
            content_type = "application/octet-stream"
            with open(path, "rb") as f:
                response = f.read()
    return HttpResponse(response, content_type=content_type)


def displayable_links_js(request, template_name="admin/displayable_links.js"):
    """
    Renders a list of url/title pairs for all ``Displayable`` subclass
    instances into JavaScript that's used to populate a list of links
    in TinyMCE.
    """
    links = []
    if "shuyucms.pages" in settings.INSTALLED_APPS:
        from shuyucms.pages.models import Page

        is_page = lambda obj: isinstance(obj, Page)
    else:
        is_page = lambda obj: False
    # For each item's title, we use its model's verbose_name, but in the
    # case of Page subclasses, we just use "Page", and then sort the items
    # by whether they're a Page subclass or not, then by their URL.
    for url, obj in Displayable.objects.url_map(for_user=request.user).items():
        title = getattr(obj, "titles", obj.title)
        real = hasattr(obj, "id")
        page = is_page(obj)
        if real:
            verbose_name = _("Page") if page else obj._meta.verbose_name
            title = "%s: %s" % (verbose_name, title)
        links.append((not page and real, url, title))
    context = {"links": [link[1:] for link in sorted(links)]}
    content_type = "text/javascript"
    return render(request, template_name, context, content_type=content_type)


@requires_csrf_token
def page_not_found(request, template_name="errors/404.html"):
    """
    Mimics Django's 404 handler but with a different template path.
    """
    context = RequestContext(request, {
        "STATIC_URL": settings.STATIC_URL,
        "request_path": request.path,
    })
    t = get_template(template_name)
    return HttpResponseNotFound(t.render(context))


@requires_csrf_token
def server_error(request, template_name="errors/500.html"):
    """
    Mimics Django's error handler but adds ``STATIC_URL`` to the
    context.
    """
    context = RequestContext(request, {"STATIC_URL": settings.STATIC_URL})
    t = get_template(template_name)
    return HttpResponseServerError(t.render(context))
