# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelines', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='slide',
            options={
                'ordering': ('start_date', 'start_time'),
                'verbose_name': 'Slide',
                'verbose_name_plural': 'Slides'
            },
        ),

        migrations.AlterModelOptions(
            name='timelineslide',
            options={
                'ordering': ('timeline', 'slide__start_date', 'slide__start_time', 'order'),
                'verbose_name': 'Timeline Slide',
                'verbose_name_plural': 'Timeline Slides'
            },
        ),
        migrations.AddField(
            model_name='timelineslide',
            name='order',
            field=models.PositiveIntegerField(default=b'1', help_text='Used to order within the same date.', verbose_name='order'),
        ),
        migrations.AlterField(
            model_name='timelineslide',
            name='timeline',
            field=models.ForeignKey(related_name='events', to='timelines.Timeline'),
        ),

        migrations.AlterField(
            model_name='timeline',
            name='eras',
            field=models.ManyToManyField(to='timelines.Era', blank=True),
        ),
        migrations.AddField(
            model_name='timeline',
            name='content',
            field=models.TextField(null=True, verbose_name='content', blank=True),
        ),
        migrations.AddField(
            model_name='timeline',
            name='description',
            field=models.TextField(help_text='This content appears in metadata and search.', null=True, verbose_name='description', blank=True),
        ),

    ]
