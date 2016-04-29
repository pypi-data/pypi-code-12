# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=512, verbose_name='name')),
                ('identifier', models.SlugField(unique=True, max_length=512, verbose_name='identifier')),
            ],
            options={
                'ordering': ('name', 'identifier'),
                'verbose_name': ('image collection',),
                'verbose_name_plural': ('image collections',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageSlide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'image_slides', verbose_name='image')),
                ('caption', models.CharField(help_text='This text is displayed on top of the image or as its description.', max_length=256, verbose_name='caption', blank=True)),
                ('alt_text', models.CharField(help_text="This will go into the ``alt`` attribute of the image's HTML markup.", max_length=128, verbose_name='alt text', blank=True)),
                ('link', models.URLField(help_text='Enter URL, that the image should link to. (not required)', verbose_name='link')),
                ('start_date', models.DateTimeField(null=True, verbose_name='publish date', blank=True)),
                ('end_date', models.DateTimeField(null=True, verbose_name='unpublish date', blank=True)),
                ('collection', models.ForeignKey(related_name='images', verbose_name='image collection', to='image_collection.ImageCollection')),
            ],
            options={
                'ordering': ('collection', 'start_date', 'end_date', 'alt_text'),
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
            bases=(models.Model,),
        ),
    ]
