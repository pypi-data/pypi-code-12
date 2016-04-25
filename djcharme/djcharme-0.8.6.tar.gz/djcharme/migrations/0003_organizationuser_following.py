# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djcharme', '0002_remove_organizationuser_following'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationuser',
            name='following',
            field=models.BooleanField(default=False, help_text=b'Send emails about any annotation created or altered by the organization.', verbose_name=b'email changes'),
            preserve_default=True,
        ),
    ]
