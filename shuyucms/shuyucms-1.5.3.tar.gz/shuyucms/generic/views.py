# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from json import dumps

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.comments.models import Comment
from django.contrib.messages import error
from django.core.urlresolvers import reverse
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from future.builtins import str
from shuyucms.conf import settings
from shuyucms.generic.forms import ThreadedCommentForm
from shuyucms.generic.models import Keyword
from shuyucms.utils.models import get_model
from shuyucms.utils.views import render, is_spam


@staff_member_required
def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the
    admin, and returns their IDs for use when saving a model with a
    keywords field.
    """
    keyword_ids, titles = [], []
    for title in request.POST.get("text_keywords", "").split(","):
        title = "".join([c for c in title if c.isalnum() or c in "- "]).strip()
        if title:
            kw, created = Keyword.objects.get_or_create_iexact(title=title)
            keyword_id = str(kw.id)
            if keyword_id not in keyword_ids:
                keyword_ids.append(keyword_id)
                titles.append(title)
    return HttpResponse("%s|%s" % (",".join(keyword_ids), ", ".join(titles)))


def initial_validation(request, prefix):
    """
    Returns the related model instance and post data to use in the
    comment views below.

    Both comments have a ``prefix_ACCOUNT_REQUIRED``
    setting. If this is ``True`` and the user is unauthenticated, we
    store their post data in their session, and redirect to login with
    the view's url (also defined by the prefix arg) as the ``next``
    param. We can then check the session data once they log in,
    and complete the action authenticated.

    On successful post, we pass the related object and post data back,
    which may have come from the session, for each of the comments
    view functions to deal with as needed.
    """
    post_data = request.POST
    settings.use_editable()
    login_required_setting_name = prefix.upper() + "S_ACCOUNT_REQUIRED"
    posted_session_key = "unauthenticated_" + prefix
    redirect_url = ""
    if getattr(settings, login_required_setting_name, False):
        if not request.user.is_authenticated():
            request.session[posted_session_key] = request.POST
            error(request, _("You must be logged in. Please log in or "
                             "sign up to complete this action."))
            redirect_url = "%s?next=%s" % (settings.LOGIN_URL, reverse(prefix))
        elif posted_session_key in request.session:
            post_data = request.session.pop(posted_session_key)
    if not redirect_url:
        try:
            model = get_model(*post_data.get("content_type", "").split(".", 1))
            obj = model.objects.get(id=post_data.get("object_pk", None))
        except (TypeError, ObjectDoesNotExist, LookupError):
            redirect_url = "/"
    if redirect_url:
        if request.is_ajax():
            return HttpResponse(dumps({"location": redirect_url}))
        else:
            return redirect(redirect_url)
    return obj, post_data


def comment(request, template="generic/comments.html"):
    """
    Handle a ``ThreadedCommentForm`` submission and redirect back to its
    related object.
    """
    response = initial_validation(request, "comment")
    if isinstance(response, HttpResponse):
        return response
    obj, post_data = response
    form = ThreadedCommentForm(request, obj, post_data)
    if form.is_valid():
        # 垃圾评论相关
        # url = obj.get_absolute_url()
        # if is_spam(request, form, url):
        # return redirect(url)
        comment = form.save(request)

        response = redirect(comment.get_absolute_url())
        return response
    elif request.is_ajax() and form.errors:
        return HttpResponse(dumps({"errors": form.errors}))
    # Show errors with stand-alone comment form.
    context = {"obj": obj, "posted_comment_form": form}
    response = render(request, template, context)
    return response


@csrf_protect
@require_GET
def comment_support(request, cid):
    """
    Support a comment
    HTTP GET is required,ajax json is supported
    """
    cmts = Comment.objects.filter(id=cid)
    if cmts:
        cobj = cmts[0]
        cobj.support_count += 1
        cobj.save()
        status = {'status': 1}
    else:
        status = {'status': 0}
    return HttpResponse(dumps(status), content_type='application/json')
