# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PiwikConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('piwik_url', models.URLField(default=b'')),
                ('piwik_site_id', models.PositiveSmallIntegerField()),
                ('site', models.OneToOneField(related_name='piwik_configuration', to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
