# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
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
                ('start_date', timelines.fields.HistoricalDateField(verbose_name='start date')),
                ('end_date', timelines.fields.HistoricalDateField(verbose_name='end date')),
                ('headline', models.CharField(max_length=255, verbose_name='label', blank=True)),
            ],
            options={
                'ordering': ('timeline', 'start_date'),
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
                ('background_color', timelines.fields.ColorField(default=b'ffffff', max_length=10, verbose_name='background color')),
                ('headline_ovr', models.CharField(help_text=b'Used for URL or override for selected object.', max_length=255, null=True, verbose_name='headline', blank=True)),
                ('text_ovr', models.TextField(help_text=b'Used for URL or override for selected object.', null=True, verbose_name='text', blank=True)),
                ('credit_ovr', models.CharField(help_text=b'Used for URL or override for selected object.', max_length=255, null=True, verbose_name='credit', blank=True)),
                ('caption_ovr', models.TextField(help_text=b'Used for URL or override for selected object.', null=True, verbose_name='caption', blank=True)),
                ('start_date', timelines.fields.HistoricalDateField(verbose_name='start date')),
                ('start_time', models.TimeField(null=True, verbose_name='start time', blank=True)),
                ('end_date', timelines.fields.HistoricalDateField(null=True, verbose_name='end date', blank=True)),
                ('end_time', models.TimeField(null=True, verbose_name='end time', blank=True)),
                ('background_image', models.ForeignKey(verbose_name='background image', blank=True, to=swapper.get_model_name('timelines', 'background_image'), null=True)),
                ('content_type', models.ForeignKey(related_name='+', verbose_name='media content type', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('timeline', 'start_date'),
                'verbose_name': 'Slide',
                'verbose_name_plural': 'Slides',
            },
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255, null=True, verbose_name='media URL', blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='media ID', blank=True)),
                ('use_media_as_background', models.BooleanField(default=False, verbose_name='use media as background')),
                ('background_color', timelines.fields.ColorField(default=b'ffffff', max_length=10, verbose_name='background color')),
                ('headline_ovr', models.CharField(help_text=b'Used for URL or override for selected object.', max_length=255, null=True, verbose_name='headline', blank=True)),
                ('text_ovr', models.TextField(help_text=b'Used for URL or override for selected object.', null=True, verbose_name='text', blank=True)),
                ('credit_ovr', models.CharField(help_text=b'Used for URL or override for selected object.', max_length=255, null=True, verbose_name='credit', blank=True)),
                ('caption_ovr', models.TextField(help_text=b'Used for URL or override for selected object.', null=True, verbose_name='caption', blank=True)),
                ('scale', models.CharField(default=b'human', help_text='The cosmological scale is required to handle dates in the very distant past or future.', max_length=15, verbose_name='scale', choices=[(b'human', 'human'), (b'cosmological', 'cosmological')])),
                ('slug', models.SlugField(default=b'', help_text='Slug must be set manually if headline is not set.', max_length=255, verbose_name='slug')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False, verbose_name='published')),
                ('publish_date', models.DateTimeField(null=True, verbose_name='publish date', blank=True)),
                ('background_image', models.ForeignKey(verbose_name='background image', blank=True, to=swapper.get_model_name('timelines', 'background_image'), null=True)),
                ('content_type', models.ForeignKey(related_name='+', verbose_name='media content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('eras', models.ManyToManyField(to='timelines.Era')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimelineSlide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(help_text='If present, Timeline will organize events with the same value for group to be in the same row or adjacent rows, separate from events in other groups.', max_length=255, null=True, verbose_name='group', blank=True)),
                ('slide', models.ForeignKey(to='timelines.Slide')),
                ('timeline', models.ForeignKey(to='timelines.Timeline')),
            ],
            options={
                'ordering': ('timeline', 'slide__startdate'),
                'verbose_name': 'TimelineSlide',
                'verbose_name_plural': 'TimelineSlides',
            },
        ),
        migrations.AddField(
            model_name='timeline',
            name='slides',
            field=models.ManyToManyField(to='timelines.Slide', through='timelines.TimelineSlide'),
        ),
    ]
