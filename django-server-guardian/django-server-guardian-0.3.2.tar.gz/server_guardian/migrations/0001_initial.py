# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='server name', blank=True)),
                ('url', models.URLField(help_text=b'The URL, that the guardian API is available under.', verbose_name='API URL')),
                ('token', models.CharField(help_text=b'Add this to your client server settings as "SERVER_GUARDIAN_SECURITY_TOKEN".', max_length=256, verbose_name='token')),
                ('response_body', models.TextField(verbose_name='server response', blank=True)),
                ('status_code', models.PositiveIntegerField(null=True, verbose_name='server response status code', blank=True)),
                ('last_updated', models.DateTimeField(null=True, verbose_name='last updated', blank=True)),
            ],
        ),
    ]
