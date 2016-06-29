# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archivevalley', '0087_auto_20160511_1326'),
        ('postman', '0004_remove_message_subject1'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='avatar',
            field=models.ForeignKey(to='archivevalley.UserProfile', related_name='message_avatar', verbose_name='avatar', null=True, blank=True),
        ),
    ]
