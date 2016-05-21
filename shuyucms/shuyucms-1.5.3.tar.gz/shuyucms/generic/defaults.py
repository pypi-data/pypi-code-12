from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from shuyucms.conf import register_setting

generic_comments = getattr(settings, "COMMENTS_APP", "") == "shuyucms.generic"

if generic_comments:
    register_setting(
        name="COMMENTS_ACCOUNT_REQUIRED",
        label=_("Accounts required for commenting"),
        description=_("If ``True``, users must log in to comment."),
        editable=True,
        default=False,
    )

    register_setting(
        name="COMMENTS_DEFAULT_APPROVED",
        label=_("Auto-approve comments"),
        description=_("If ``True``, built-in comments are approved by "
                      "default."),
        editable=True,
        default=True,
    )

    register_setting(
        name="COMMENT_FILTER",
        description=_("Dotted path to the function to call on a comment's "
                      "value before it is rendered to the template."),
        editable=False,
        default=None,
    )

    register_setting(
        name="COMMENTS_NOTIFICATION_EMAILS",
        label=_("Comment notification email addresses"),
        description=_("A comma separated list of email addresses that "
                      "will receive an email notification each time a "
                      "new comment is posted on the site."),
        editable=False,
        default="",
    )

    register_setting(
        name="COMMENTS_NUM_LATEST",
        label=_("Admin comments"),
        description=_("Number of latest comments shown in the admin "
                      "dashboard."),
        editable=True,
        default=20,
    )

    register_setting(
        name="COMMENTS_REMOVED_VISIBLE",
        label=_("Show removed comments"),
        description=_("If ``True``, comments that have ``removed`` "
                      "checked will still be displayed, but replaced "
                      "with a ``removed`` message."),
        editable=True,
        default=False,
    )
