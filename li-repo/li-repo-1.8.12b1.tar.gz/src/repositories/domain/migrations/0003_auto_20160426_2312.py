# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='logradouro',
            name='complemento',
            field=models.CharField(max_length=256, null=True, db_column=b'complemento'),
        ),
        migrations.AddField(
            model_name='logradouro',
            name='logradouro',
            field=models.CharField(max_length=256, null=True, db_column=b'logradouro'),
        ),
        migrations.AddField(
            model_name='logradouro',
            name='tipo',
            field=models.CharField(max_length=256, null=True, db_column=b'tipo_log'),
        ),
        migrations.AlterField(
            model_name='idioma',
            name='pais',
            field=models.ForeignKey(related_name='idiomas', default=None, to='domain.Pais', null=True),
        ),
        migrations.AlterField(
            model_name='logradouro',
            name='bairro',
            field=models.CharField(max_length=256, null=True, db_column=b'bairro'),
        ),
        migrations.AlterField(
            model_name='logradouro',
            name='cep_fim',
            field=models.IntegerField(null=True, db_column=b'cep8_fim'),
        ),
        migrations.AlterField(
            model_name='logradouro',
            name='cep_ini',
            field=models.IntegerField(null=True, db_column=b'cep8_ini'),
        ),
        migrations.AlterField(
            model_name='logradouro',
            name='cep_log',
            field=models.IntegerField(null=True, db_column=b'cep8_log'),
        ),
        migrations.AlterField(
            model_name='logradouro',
            name='uf',
            field=models.CharField(max_length=2, null=True, db_column=b'uf_log'),
        ),
    ]
