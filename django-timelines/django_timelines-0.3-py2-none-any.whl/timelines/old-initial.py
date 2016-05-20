# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import colorfield.fields
import timelines.fields
import swapper


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        swapper.dependency('timelines', 'background_image')
    ]

    operations = [
        migrations.CreateModel(
            name='Era',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', timelines.fields.HistoricalDateField()),
                ('end_date', timelines.fields.HistoricalDateField()),
                ('headline', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'verbose_name': 'Era',
                'verbose_name_plural': 'Eras',
            },
        ),
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255, null=True, verbose_name='media URL', blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='media ID', blank=True)),
                ('use_media_as_background', models.BooleanField(default=False, verbose_name='use media as background')),
                ('background_color', colorfield.fields.ColorField(default=b'#ffffff', max_length=10)),
                ('headline_ovr', models.CharField(max_length=255, null=True, verbose_name='headline', blank=True)),
                ('text_ovr', models.TextField(null=True, verbose_name='text', blank=True)),
                ('credit_ovr', models.CharField(max_length=255, null=True, verbose_name='credit', blank=True)),
                ('caption_ovr', models.TextField(null=True, verbose_name='caption', blank=True)),
                ('start_date', timelines.fields.HistoricalDateField(verbose_name='start date')),
                ('start_time', models.TimeField(null=True, verbose_name='start time', blank=True)),
                ('end_date', timelines.fields.HistoricalDateField(null=True, verbose_name='end date', blank=True)),
                ('end_time', models.TimeField(null=True, verbose_name='end time', blank=True)),
                ('group', models.CharField(help_text='If present, Timeline will organize events with the same value for group to be in the same row or adjacent rows, separate from events in other groups.', max_length=255, null=True, verbose_name='group', blank=True)),
                ('background_image', models.ForeignKey(verbose_name='background image', blank=True, to=swapper.get_model_name('timelines', 'background_image'), null=True)),
                ('content_type', models.ForeignKey(related_name='+', verbose_name='media content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255, null=True, verbose_name='media URL', blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='media ID', blank=True)),
                ('use_media_as_background', models.BooleanField(default=False, verbose_name='use media as background')),
                ('background_color', colorfield.fields.ColorField(default=b'#ffffff', max_length=10)),
                ('headline_ovr', models.CharField(max_length=255, null=True, verbose_name='headline', blank=True)),
                ('slug', models.SlugField(default=b'', max_length=255, verbose_name='slug')),
                ('text_ovr', models.TextField(null=True, verbose_name='text', blank=True)),
                ('credit_ovr', models.CharField(max_length=255, null=True, verbose_name='credit', blank=True)),
                ('caption_ovr', models.TextField(null=True, verbose_name='caption', blank=True)),
                ('scale', models.CharField(default=b'human', help_text='The cosmological scale is required to handle dates in the very distant past or future.', max_length=15, verbose_name='scale', choices=[(b'human', 'human'), (b'cosmological', 'cosmological')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False, verbose_name='published')),
                ('publish_date', models.DateTimeField(null=True, verbose_name='publish date', blank=True)),
                ('background_image', models.ForeignKey(verbose_name='background image', blank=True, to=swapper.get_model_name('timelines', 'background_image'), null=True)),
                ('content_type', models.ForeignKey(related_name='+', verbose_name='media content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='slide',
            name='timeline',
            field=models.ForeignKey(related_name='events', to='timelines.Timeline'),
        ),
        migrations.AddField(
            model_name='era',
            name='timeline',
            field=models.ForeignKey(related_name='eras', to='timelines.Timeline'),
        ),
    ]
