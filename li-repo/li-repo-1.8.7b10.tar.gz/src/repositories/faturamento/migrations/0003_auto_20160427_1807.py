# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamento', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadoscobranca',
            name='razao_social',
            field=models.TextField(null=True, db_column=b'dados_cobranca_razao_social'),
        ),
    ]
