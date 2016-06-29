# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archivevalley', '0091_userprofile_user_type'),
        ('postman', '0020_remove_message_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='user_profile',
            field=models.OneToOneField(null=True, to='archivevalley.UserProfile', blank=True),
        ),
        migrations.AddField(
            model_name='message',
            name='yes_no',
            field=models.CharField(null=True, max_length=20, default='YES', choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")]),
        ),
    ]
