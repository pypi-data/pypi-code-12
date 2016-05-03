# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_pypiwik', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='piwikconfiguration',
            name='piwik_token_auth',
            field=models.CharField(max_length=250, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='piwikconfiguration',
            name='piwik_url',
            field=models.URLField(default=b'http://lalalal.local/piwik/'),
            preserve_default=True,
        ),
    ]
