# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import feincms.module.medialibrary.fields


class Migration(migrations.Migration):

    dependencies = [
        ('medialibrary', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryContainer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('_order', models.IntegerField(default=0, verbose_name='Order')),
                ('title', models.CharField(verbose_name='Title', max_length=300)),
            ],
            options={
                'verbose_name': 'Simple Gallery',
                'ordering': ['_order', 'title'],
                'verbose_name_plural': 'Simple Galleries',
            },
        ),
        migrations.CreateModel(
            name='GalleryElement',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('_order', models.IntegerField(default=0, verbose_name='Order')),
                ('title', models.CharField(verbose_name='Title', blank=True, max_length=100, null=True)),
                ('subtitle', models.CharField(verbose_name='Subtitle', blank=True, max_length=200, null=True)),
                ('description', models.TextField(verbose_name='Description', blank=True, null=True)),
                ('url', models.CharField(verbose_name='URL', blank=True, max_length=2048, null=True)),
                ('container', models.ForeignKey(verbose_name='Gallery', null=True, to='feincms_simplegallery.GalleryContainer', blank=True, related_name='container_elements')),
                ('mediafile', feincms.module.medialibrary.fields.MediaFileForeignKey(null=True, to='medialibrary.MediaFile', help_text='Image', blank=True, related_name='+')),
            ],
            options={
                'verbose_name': 'Gallery Element',
                'ordering': ['_order', 'title'],
                'verbose_name_plural': 'Gallery Elements',
            },
        ),
    ]
