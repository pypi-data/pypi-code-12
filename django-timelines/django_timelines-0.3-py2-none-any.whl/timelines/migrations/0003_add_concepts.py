# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0001_initial'),
        ('timelines', '0002_misc_model_tweaks'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='concepts',
            field=taggit.managers.TaggableManager(to='concepts.Concept', through='concepts.ConceptItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
