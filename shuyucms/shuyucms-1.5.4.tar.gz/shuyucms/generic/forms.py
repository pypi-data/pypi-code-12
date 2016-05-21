# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.signals import comment_was_posted
from django.utils.safestring import mark_safe
from future.builtins import str, zip
from shuyucms.core.forms import Html5Mixin
from shuyucms.generic.models import Keyword, ThreadedComment
from shuyucms.utils.views import ip_for_request


class KeywordsWidget(forms.MultiWidget):
    """
    Form field for the ``KeywordsField`` generic relation field. Since
    the admin with model forms has no form field for generic
    relations, this form field provides a single field for managing
    the keywords. It contains two actual widgets, a text input for
    entering keywords, and a hidden input that stores the ID of each
    ``Keyword`` instance.

    The attached JavaScript adds behaviour so that when the form is
    submitted, an AJAX post is made that passes the list of keywords
    in the text input, and returns a list of keyword IDs which are
    then entered into the hidden input before the form submits. The
    list of IDs in the hidden input is what is used when retrieving
    an actual value from the field for the form.
    """

    class Media:
        js = ("shuyucms/js/admin/keywords_field.js",)

    def __init__(self, attrs=None):
        """
        Setup the text and hidden form field widgets.
        """
        widgets = (forms.HiddenInput,
                   forms.TextInput(attrs={"class": "vTextField"}))
        super(KeywordsWidget, self).__init__(widgets, attrs)
        self._ids = []

    def decompress(self, value):
        """
        Takes the sequence of ``AssignedKeyword`` instances and splits
        them into lists of keyword IDs and titles each mapping to one
        of the form field widgets.
        """
        if hasattr(value, "select_related"):
            keywords = [a.keyword for a in value.select_related("keyword")]
            if keywords:
                keywords = [(str(k.id), k.title) for k in keywords]
                self._ids, words = list(zip(*keywords))
                return (",".join(self._ids), ", ".join(words))
        return ("", "")

    def format_output(self, rendered_widgets):
        """
        Wraps the output HTML with a list of all available ``Keyword``
        instances that can be clicked on to toggle a keyword.
        """
        rendered = super(KeywordsWidget, self).format_output(rendered_widgets)
        links = ""
        # 下面只返回前300个，非池，2015-0820
        objs = Keyword.objects.all().order_by("-assigned_num")[:300]
        for keyword in objs:
            prefix = "+" if str(keyword.id) not in self._ids else "-"
            links += ("<a href='#'>%s%s</a>" % (prefix, str(keyword)))
        rendered += '<p style="margin: 5px 0px 2px 130px;color: #888;">下面选取频率最高的前300个标签；也可以直接输入新标签，用，分隔</p>'
        rendered += mark_safe("<p class='keywords-field'>%s</p>" % links)
        return rendered

    def value_from_datadict(self, data, files, name):
        """
        Return the comma separated list of keyword IDs for use in
        ``KeywordsField.save_form_data()``.
        """
        return data.get("%s_0" % name, "")


class ThreadedCommentForm(CommentForm, Html5Mixin):
    def __init__(self, request, *args, **kwargs):
        kwargs.setdefault("initial", {})
        super(ThreadedCommentForm, self).__init__(*args, **kwargs)

    def get_comment_model(self):
        """
        Use the custom comment model instead of the built-in one.
        """
        return ThreadedComment

    def save(self, request):
        """
        Saves a new comment and sends any notification emails.
        """
        comment = self.get_comment_object()
        if request.user.is_authenticated():
            comment.user = request.user
        comment.ip_address = ip_for_request(request)
        comment.replied_to_id = self.data.get("replied_to")
        comment.save()
        comment_was_posted.send(sender=comment.__class__, comment=comment, request=request)
        return comment
