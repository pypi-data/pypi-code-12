# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True)),
                ('order_by', models.CharField(max_length=255, blank=True)),
                ('template_name', models.CharField(max_length=255, blank=True)),
                ('distinct', models.BooleanField(default=False)),
                ('base_object', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='ReportColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('path', models.CharField(max_length=255)),
                ('aggregation', models.CharField(blank=True, max_length=10, choices=[(b'sum', b'Sum'), (b'count', b'Count'), (b'min', b'Minimum'), (b'max', b'Maximum')])),
                ('sort_order', models.SmallIntegerField(default=0)),
                ('rollup', models.BooleanField(default=False)),
                ('format', models.CharField(max_length=255, blank=True)),
                ('alignment', models.CharField(default=b'left', max_length=10, choices=[(b'right', b'Right'), (b'center', b'Center'), (b'left', b'Left')])),
                ('report', models.ForeignKey(related_name='columns', to='query_reports.QueryReport')),
            ],
            options={
                'ordering': ('sort_order',),
            },
        ),
        migrations.CreateModel(
            name='ReportFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exclude', models.BooleanField(default=False)),
                ('path', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('sort_order', models.SmallIntegerField(default=0)),
                ('report', models.ForeignKey(related_name='filters', to='query_reports.QueryReport')),
            ],
        ),
        migrations.CreateModel(
            name='ReportVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('required', models.BooleanField(default=False)),
                ('type', models.CharField(max_length=255, choices=[(b'value', b'Value'), (b'date', b'Date')])),
                ('initial', models.CharField(max_length=255, blank=True)),
                ('report', models.ForeignKey(related_name='variables', to='query_reports.QueryReport')),
            ],
        ),
    ]
