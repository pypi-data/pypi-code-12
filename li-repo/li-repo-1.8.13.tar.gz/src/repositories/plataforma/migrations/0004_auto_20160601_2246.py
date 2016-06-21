# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0003_auto_20160426_2259'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'feature_id')),
                ('name', models.TextField(db_column=b'feature_name')),
                ('code', models.TextField(db_column=b'feature_code')),
                ('status', models.TextField(db_column=b'feature_status', choices=[(b'local', b'Local'), (b'development', b'Development'), (b'staging', b'Staging'), (b'production', b'Production'), (b'beta', b'Beta')])),
            ],
            options={
                'db_table': 'plataforma"."tb_feature',
                'verbose_name': 'Feature',
                'verbose_name_plural': 'Features',
            },
        ),
        migrations.RenameField(
            model_name='conta',
            old_name='nome_loja',
            new_name='nome',
        ),
        migrations.AddField(
            model_name='conta',
            name='beta_tester',
            field=models.BooleanField(default=False, db_column=b'conta_beta_tester'),
        ),
    ]
