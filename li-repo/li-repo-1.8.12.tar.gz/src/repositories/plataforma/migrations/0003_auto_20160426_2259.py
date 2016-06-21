# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0002_auto_20160401_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='url_termo',
            field=models.CharField(max_length=255, null=True, verbose_name='URL Termo de uso', db_column=b'contrato_url_termo'),
        ),
        migrations.AlterField(
            model_name='parceiro',
            name='data_contrato',
            field=models.DateTimeField(null=True, db_column=b'parceiro_data_contrato'),
        ),
    ]
