# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leonid', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeonidFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='name')),
                ('content', models.TextField(default='', verbose_name='content', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'leonid file',
                'verbose_name_plural': 'leonid files',
            },
        ),
    ]
