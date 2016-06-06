# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0002_auto_20160606_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='integrationhistory',
            name='model_selected',
            field=models.CharField(max_length=50, db_column=b'integration_history_model_selected'),
        ),
        migrations.AlterField(
            model_name='integrationhistory',
            name='status',
            field=models.CharField(default=b'WAIT', max_length=35, db_column=b'integration_history_status', choices=[('WAIT', 'Aguardando envio para {}'), ('QUEUE', 'Em fila para {}'), ('RETRY', 'Nova tentativa para {}'), ('SUCCESS', 'Integrado com sucesso para {}'), ('FAIL', '{} n\xe3o aceitou os dados'), ('ERROR', 'Ocorreu um erro no envio')]),
        ),
        migrations.AlterField(
            model_name='modelintegration',
            name='model_selected',
            field=models.CharField(max_length=50, db_column=b'model_integration_model_selected'),
        ),
    ]
