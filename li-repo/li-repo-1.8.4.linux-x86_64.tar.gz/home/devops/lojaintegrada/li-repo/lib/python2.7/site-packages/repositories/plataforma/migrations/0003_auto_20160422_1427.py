# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0002_auto_20160401_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimportrelation',
            name='status',
            field=models.TextField(default=b'created', verbose_name='Resultado da Importa\xe7\xe3o', db_column=b'produto_importacao_status', choices=[(b'created', 'Produto criado'), (b'updated', 'Produto atualizado')]),
        ),
    ]
