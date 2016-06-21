# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cfblog', '0003_auto_20151126_1212'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ('-publish',), 'get_latest_by': 'publish', 'permissions': (('can_publish', 'Can Publish Posts'),)},
        ),
    ]
