from django_comments.models import Comment, COMMENT_MAX_LENGTH
from django_comments.models import CommentFlag
from django.dispatch import receiver
from django_comments.signals import comment_was_flagged
from django.conf import settings
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


class MoloComment(MPTTModel, Comment):
    """
    Threaded comments - Add support for the parent comment store
    and MPTT traversal
    """

    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')

    class MPTTMeta:
        # comments on one level will be ordered by date of creation
        order_insertion_by = ['submit_date']

    class Meta:
        app_label = 'commenting'
        ordering = ['-tree_id', 'submit_date']

    def flag_count(self, flag):
        return self.flags.filter(flag=flag).count()


@receiver(comment_was_flagged, sender=MoloComment)
def remove_comment_if_flag_limit(sender, comment, flag, created, **kwargs):
    # Auto removal is off by default
    try:
        threshold_count = settings.COMMENTS_FLAG_THRESHHOLD
    except AttributeError:
        return

    if flag.flag != CommentFlag.SUGGEST_REMOVAL:
        return
    # Don't remove comments that have been approved by a moderator
    if (comment.flag_count(CommentFlag.MODERATOR_APPROVAL) > 0):
        return

    if (comment.flag_count(CommentFlag.SUGGEST_REMOVAL) >= threshold_count):
        comment.is_removed = True
        comment.save()


class CannedResponse(models.Model):
    response_header = models.CharField(max_length=500, blank=False)
    response = models.TextField(max_length=COMMENT_MAX_LENGTH, blank=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.response_header

    class Meta:
        verbose_name_plural = 'Canned responses'
        app_label = 'commenting'
        ordering = ['response_header', 'response']
