# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamento', '0003_auto_20160427_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadoscobranca',
            name='cnpj',
            field=models.TextField(null=True, db_column=b'dados_cobranca_cnpj'),
        ),
        migrations.AlterField(
            model_name='dadoscobranca',
            name='cpf',
            field=models.TextField(null=True, db_column=b'dados_cobranca_cpf'),
        ),
    ]
