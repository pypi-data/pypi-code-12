# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Setting name. Since it will be accessed from python code, the syntax is the same as for any valid python identifier', max_length=255, verbose_name='Name', validators=[django.core.validators.RegexValidator(b'^[a-zA-Z_][a-zA-Z0-9_]+', 'Setting name must consist in a-z letters, numbers, and underscores, and cannot start with a number')])),
                ('allow_null', models.BooleanField(default=False, help_text='Check this to allow null value in this setting.', verbose_name='Allow null value')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BooleanDynamicSetting',
            fields=[
                ('dynamicsetting_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dynsettings.DynamicSetting')),
                ('value', models.NullBooleanField(help_text='Setting value. It must be marked, not marked, or undefined.', verbose_name='Value')),
            ],
            options={
                'abstract': False,
            },
            bases=('dynsettings.dynamicsetting',),
        ),
        migrations.CreateModel(
            name='DecimalDynamicSetting',
            fields=[
                ('dynamicsetting_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dynsettings.DynamicSetting')),
                ('value', models.DecimalField(decimal_places=16, max_digits=32, blank=True, help_text='Setting value. It must be a valid numeric value.', null=True, verbose_name='Value')),
            ],
            options={
                'abstract': False,
            },
            bases=('dynsettings.dynamicsetting',),
        ),
        migrations.CreateModel(
            name='IntegerDynamicSetting',
            fields=[
                ('dynamicsetting_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dynsettings.DynamicSetting')),
                ('value', models.IntegerField(help_text='Setting value. It must be a valid (signed, 4-byte) integer value.', null=True, verbose_name='Value', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('dynsettings.dynamicsetting',),
        ),
        migrations.CreateModel(
            name='LongTextDynamicSetting',
            fields=[
                ('dynamicsetting_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dynsettings.DynamicSetting')),
                ('value', models.TextField(help_text='Setting value.', max_length=16777215, null=True, blank=True, verbose_name='Value')),
            ],
            options={
                'abstract': False,
            },
            bases=('dynsettings.dynamicsetting',),
        ),
        migrations.CreateModel(
            name='ShortTextDynamicSetting',
            fields=[
                ('dynamicsetting_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dynsettings.DynamicSetting')),
                ('value', models.CharField(help_text='Setting value.', max_length=255, null=True, verbose_name='Value', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('dynsettings.dynamicsetting',),
        ),
        migrations.AddField(
            model_name='dynamicsetting',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_dynsettings.dynamicsetting_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
