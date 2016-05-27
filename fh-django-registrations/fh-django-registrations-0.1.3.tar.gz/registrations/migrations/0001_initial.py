# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated')),
                ('verification_code', models.CharField(max_length=255, null=True, verbose_name='Verification Code')),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email Address', db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Email Registration',
                'verbose_name_plural': 'Email Registrations',
            },
        ),
        migrations.CreateModel(
            name='SMSRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated')),
                ('verification_code', models.CharField(max_length=255, null=True, verbose_name='Verification Code')),
                ('mobile_phone', models.CharField(unique=True, max_length=12, verbose_name='Mobile Phone', db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SMS Registration',
                'verbose_name_plural': 'SMS Registrations',
            },
        ),
    ]
