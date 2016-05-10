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
            name='SessionInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('key', models.CharField(max_length=32, verbose_name='\u041a\u043b\u044e\u0447', db_index=True)),
                ('prefix', models.CharField(default='default', max_length=16, db_index=True)),
                ('active', models.BooleanField(default=True)),
                ('user_ip', models.IPAddressField(default='127.0.0.1', db_index=True)),
                ('user_agent', models.TextField(default=None, null=True, blank=True)),
                ('user_agent_md5', models.CharField(default=None, max_length=32, null=True, blank=True)),
                ('user', models.ForeignKey(related_name='sessions', verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': '\u0421\u0435\u0441\u0441\u0438\u0438',
            },
        ),
        migrations.AlterUniqueTogether(
            name='sessioninfo',
            unique_together=set([('prefix', 'key')]),
        ),
    ]
