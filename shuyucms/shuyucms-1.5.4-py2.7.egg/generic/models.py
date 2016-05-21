# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.comments.models import Comment
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models
from django.template.defaultfilters import truncatewords_html
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from future.builtins import str
from shuyucms.core.models import SiteRelated, Orderable
from shuyucms.generic.managers import CommentManager, KeywordManager


class ThreadedComment(Comment):
    """
    Extend the ``Comment`` model from ``django.contrib.comments`` to
    add comment threading. ``Comment`` provides its own site foreign key,
    so we can't inherit from ``SiteRelated`` in ``shuyucms.core``, and
    therefore need to set the site on ``save``. ``CommentManager``
    inherits from shuyucms's ``CurrentSiteManager``, so everything else
    site related is already provided.
    """
    replied_to = models.ForeignKey("self", null=True, editable=False, related_name="comments")
    objects = CommentManager()

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"

    def get_absolute_url(self):
        """
        Use the URL for the comment's content object, with a URL hash
        appended that references the individual comment.
        """
        url = self.content_object.get_absolute_url()
        return "%s#comment-%s" % (url, self.id)

    def save(self, *args, **kwargs):
        super(ThreadedComment, self).save(*args, **kwargs)

    ################################
    # Admin listing column methods #
    ################################

    def intro(self):
        return truncatewords_html(self.comment, 20)

    intro.allow_tags = True
    intro.short_description = _("Comment")

    def avatar_link(self):
        vars = (self.user_email, self.user_name)
        return ("<a href='mailto:%s'>%s</a>" % vars)

    avatar_link.allow_tags = True
    avatar_link.short_description = _("User")

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(),
                                        ugettext("View on site"))

    admin_link.allow_tags = True
    admin_link.short_description = ""


class Keyword(SiteRelated):
    """
    领域标签字段
    """

    objects = KeywordManager()
    title = models.CharField('名称', max_length=100, unique=True)
    parent = models.ForeignKey('self', verbose_name='上级', null=True, blank=True,
                               limit_choices_to={'id__in': [1, 2, 3, 4, 5, 6, 7]},
                               db_column='parent', related_name='+', on_delete=models.SET(''))
    assigned_num = models.IntegerField('标签频率', null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "领域标签"
        verbose_name_plural = "领域标签"

    def __unicode__(self):
        return self.title


@python_2_unicode_compatible
class AssignedKeyword(Orderable):
    """
    A ``Keyword`` assigned to a model instance.
    """

    keyword = models.ForeignKey("Keyword", verbose_name=_("Keyword"),
                                related_name="assignments")
    content_type = models.ForeignKey("contenttypes.ContentType")
    object_pk = models.IntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_pk")

    class Meta:
        verbose_name = "已分配的领域标签"
        verbose_name_plural = "已分配的领域标签"

    def __str__(self):
        return str(self.keyword)
