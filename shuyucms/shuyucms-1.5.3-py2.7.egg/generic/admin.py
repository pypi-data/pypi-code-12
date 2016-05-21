# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from shuyucms.conf import settings
from shuyucms.generic.models import ThreadedComment, AssignedKeyword, Keyword


class ThreadedCommentAdmin(CommentsAdmin):
    """
    Admin class for comments.
    """

    list_display = ("id", "user", "submit_date", "content_object", "intro", "is_removed", "support_count", "admin_link")
    list_display_links = ("user", "intro",)
    list_filter = [f for f in CommentsAdmin.list_filter if f != "site"]
    fieldsets = (
        (None, {"fields": ("user", "comment", "is_removed", "support_count")}),
    )
    search_fields = ["comment", ]

    def get_actions(self, request):
        actions = super(CommentsAdmin, self).get_actions(request)
        actions.pop("flag_comments")
        return actions

    # Disable the 'Add' action for this model, fixed a crash if you try
    # to create a comment from admin panel
    def has_add_permission(self, request):
        return False


generic_comments = getattr(settings, "COMMENTS_APP", "") == "shuyucms.generic"
if generic_comments:
    admin.site.register(ThreadedComment, ThreadedCommentAdmin)


# 删除缺失的已分配的关键词
def delnullkeywords(modeladmin, request, queryset):
    objs = AssignedKeyword.objects.all()
    for obj in objs:
        if not obj.content_object:
            obj.delete()


delnullkeywords.short_description = "删除所有缺失的 已分配的关键词（请在半夜运行）"


class AssignedKeywordAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": ["keyword", ]}),)
    list_display = ["id", "keyword", "content_object", "content_type", ]
    actions = [delnullkeywords, ]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(AssignedKeywordAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# admin.site.register(AssignedKeyword, AssignedKeywordAdmin)


class KeywordAdmin(admin.ModelAdmin):
    fieldsets = ((None, {"fields": ["title", "parent", "assigned_num"]}),)
    list_display = ["id", "title", "parent", "assigned_num"]
    raw_id_fields = ("parent",)
    search_fields = ["=title", ]


admin.site.register(Keyword, KeywordAdmin)
