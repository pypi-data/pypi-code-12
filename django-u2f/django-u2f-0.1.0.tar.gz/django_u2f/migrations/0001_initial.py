# -*- coding: utf-8 -*-
# Generated by Django 1.9b1 on 2015-11-17 22:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='U2FKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(null=True)),
                ('public_key', models.TextField()),
                ('key_handle', models.TextField()),
                ('app_id', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='u2f_keys', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
