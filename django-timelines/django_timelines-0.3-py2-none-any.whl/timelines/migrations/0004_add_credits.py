# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0001_initial'),
        ('timelines', '0003_add_concepts'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='credits',
            field=models.ForeignKey(verbose_name='timeline credits', blank=True, to='credits.CreditGroup', null=True),
        ),
    ]
