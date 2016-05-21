# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.comments.managers import CommentManager
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class BaseCommentAbstractModel(models.Model):
    """
    An abstract base class that any custom comment models probably should
    subclass.
    """

    # Content-object field
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=10, db_index=True)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    # Metadata about the comment
    # site = models.ForeignKey(Site)

    class Meta:
        abstract = True

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "comments-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )


@python_2_unicode_compatible
class Comment(BaseCommentAbstractModel):
    """
    A user comment about some object.
    """

    # Who posted this comment? If ``user`` is set then it was an authenticated
    # user; otherwise at least user_name should have been set and the comment
    # was posted by a non-authenticated user.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'),
                             blank=True, null=True, related_name="%(class)s_comments")
    # user_name = models.CharField(_("user's name"), max_length=50, blank=True)
    # user_email = models.EmailField(_("user's email address"), blank=True)
    # user_url = models.URLField(_("user's URL"), blank=True)

    comment = models.TextField(_('comment'), max_length=COMMENT_MAX_LENGTH)

    # Metadata about the comment
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    ip_address = models.GenericIPAddressField(_('IP address'), unpack_ipv4=True, blank=True, null=True)
    is_removed = models.BooleanField('是否已删除', default=False, help_text='标记为删除')
    support_count = models.IntegerField('点赞数', default=0, help_text='被点赞数目')

    # Manager
    objects = CommentManager()

    class Meta:
        db_table = "generic_comments"
        ordering = ('submit_date',)
        permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __str__(self):
        return "%s: %s..." % (self.user.username, self.comment[:50])

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = timezone.now()
        super(Comment, self).save(*args, **kwargs)

    def _get_userinfo(self):
        """
        Get a dictionary that pulls together information about the poster
        safely for both authenticated and non-authenticated comments.
        """
        if not hasattr(self, "_userinfo"):
            userinfo = {
                "name": self.user.username,
            }
            self._userinfo = userinfo
        return self._userinfo

    userinfo = property(_get_userinfo, doc=_get_userinfo.__doc__)

    def get_absolute_url(self, anchor_pattern="#c%(id)s"):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)

    def get_as_text(self):
        """
        Return this comment as plain text.  Useful for emails.
        """
        d = {
            'user': self.user.username,
            'date': self.submit_date,
            'comment': self.comment
        }
        return _('Posted by %(user)s at %(date)s\n\n%(comment)s') % d


@python_2_unicode_compatible
class CommentFlag(models.Model):
    """
    Records a flag on a comment. This is intentionally flexible; right now, a
    flag could be:

        * A "removal suggestion" -- where a user suggests a comment for (potential) removal.

        * A "moderator deletion" -- used when a moderator deletes a comment.

    You can (ab)use this model to add other flags, if needed. However, by
    design users are only allowed to flag a comment with a given flag once;
    if you want rating look elsewhere.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name="comment_flags")
    comment = models.ForeignKey(Comment, verbose_name=_('comment'), related_name="flags")
    flag = models.CharField(_('flag'), max_length=30, db_index=True)

    # Constants for flag types
    SUGGEST_REMOVAL = "removal suggestion"
    MODERATOR_DELETION = "moderator deletion"
    MODERATOR_APPROVAL = "moderator approval"

    class Meta:
        abstract = True
        unique_together = [('user', 'comment', 'flag')]
        verbose_name = _('comment flag')
        verbose_name_plural = _('comment flags')

    def __str__(self):
        return "%s flag of comment ID %s by %s" % \
               (self.flag, self.comment_id, self.user.get_username())
