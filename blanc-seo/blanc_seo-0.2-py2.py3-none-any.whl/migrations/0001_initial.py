# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, blank=True)),
                ('description', models.TextField(blank=True)),
                ('keywords', models.TextField(blank=True)),
                ('open_graph_url', models.URLField(verbose_name='URL', blank=True, help_text='Canonical URL')),
                ('open_graph_title', models.CharField(verbose_name='Title', max_length=100, blank=True)),
                ('open_graph_description', models.TextField(verbose_name='Description', blank=True)),
                ('open_graph_image', models.ImageField(upload_to='blancseo/meta', width_field='open_graph_image_width', height_field='open_graph_image_height', verbose_name='Image', help_text='1.91:1 aspect ratio, ideally 1200 x 630 or 600 x 315', blank=True)),
                ('open_graph_image_width', models.PositiveIntegerField(editable=False, null=True)),
                ('open_graph_image_height', models.PositiveIntegerField(editable=False, null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='URLMetaContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, blank=True)),
                ('description', models.TextField(blank=True)),
                ('keywords', models.TextField(blank=True)),
                ('open_graph_url', models.URLField(verbose_name='URL', blank=True, help_text='Canonical URL')),
                ('open_graph_title', models.CharField(verbose_name='Title', max_length=100, blank=True)),
                ('open_graph_description', models.TextField(verbose_name='Description', blank=True)),
                ('open_graph_image', models.ImageField(upload_to='blancseo/meta', width_field='open_graph_image_width', height_field='open_graph_image_height', verbose_name='Image', help_text='1.91:1 aspect ratio, ideally 1200 x 630 or 600 x 315', blank=True)),
                ('open_graph_image_width', models.PositiveIntegerField(editable=False, null=True)),
                ('open_graph_image_height', models.PositiveIntegerField(editable=False, null=True)),
                ('url', models.CharField(verbose_name='URL', max_length=200, help_text='Page URL without protocol or domain, eg. /about/', unique=True)),
            ],
            options={
                'verbose_name': 'URL meta content',
            },
        ),
        migrations.AlterUniqueTogether(
            name='metacontent',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
