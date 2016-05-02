# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ACPHoliday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='HolidayType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.AddField(
            model_name='acpholiday',
            name='holiday_type',
            field=models.ForeignKey(to='acp_calendar.HolidayType'),
        ),
    ]
