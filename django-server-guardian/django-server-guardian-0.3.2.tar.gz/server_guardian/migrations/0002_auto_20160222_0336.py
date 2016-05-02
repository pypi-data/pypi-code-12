# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_guardian', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('time_logged', models.DateTimeField(verbose_name='time_logged')),
                ('status', models.CharField(max_length=16, verbose_name='status', choices=[(b'OK', b'OK'), (b'WARNING', b'WARNING'), (b'DANGER', b'DANGER')])),
                ('label', models.CharField(max_length=512, verbose_name='label')),
            ],
            options={
                'ordering': ('server', 'label', '-time_logged'),
            },
        ),
        migrations.AddField(
            model_name='server',
            name='log_age',
            field=models.PositiveIntegerField(default=10, help_text='How many days the logs are kept. Set to 0 for infinite.', verbose_name='log age'),
        ),
        migrations.AddField(
            model_name='server',
            name='logging',
            field=models.BooleanField(default=False, help_text='Enable logging results to DB (recommended)', verbose_name='logging'),
        ),
        migrations.AddField(
            model_name='serverlog',
            name='server',
            field=models.ForeignKey(related_name='server_logs', verbose_name='server', to='server_guardian.Server'),
        ),
    ]
