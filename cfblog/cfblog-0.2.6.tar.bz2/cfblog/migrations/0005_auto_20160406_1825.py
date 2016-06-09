# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Q
from django.conf import settings
from django.core.management.sql import emit_post_migrate_signal


def emit_post_migrate_to_avoid_breaking_continuity(schema_editor):
    """
     This is so that running migrations together doesn't break, because
     Django adds Permissions in post_migrate signal
    """
    db_alias = schema_editor.connection.alias
    try:
        emit_post_migrate_signal(0, False, db_alias)
    except TypeError:  # Django < 1.9
        try:
            emit_post_migrate_signal(2, False, 'default', db_alias)
        except TypeError:  # Django < 1.8
            emit_post_migrate_signal([], 2, False, 'default', db_alias)


def add_publish_permission(apps, schema_editor):
    app = settings.AUTH_USER_MODEL.split('.')[0]
    User = apps.get_model(app, 'User')
    users = User.objects.filter(
        user_permissions__codename='change_content',
        user_permissions__content_type__app_label='cfblog'
    )

    Group = apps.get_model('auth', 'Group')
    groups = Group.objects.filter(
        permissions__codename='change_content',
        permissions__content_type__app_label='cfblog'
    )

    emit_post_migrate_to_avoid_breaking_continuity(schema_editor)
    Permission = apps.get_model('auth', 'Permission')
    permission = Permission.objects.get(codename='can_publish')

    for user in users.iterator():
        user.user_permissions.add(permission)

    for group in groups.iterator():
        group.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('cfblog', '0004_auto_20160406_1820'),
    ]

    operations = [
        migrations.RunPython(
            code=add_publish_permission,
            reverse_code=migrations.RunPython.noop
        )
    ]
