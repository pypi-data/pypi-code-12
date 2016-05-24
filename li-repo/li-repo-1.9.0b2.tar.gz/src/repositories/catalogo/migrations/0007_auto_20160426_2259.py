# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0006_auto_20160422_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='data_modificacao',
            field=models.DateTimeField(auto_now=True, null=True, db_column=b'grade_data_modificacao'),
        ),
        migrations.AlterField(
            model_name='gradevariacao',
            name='data_modificacao',
            field=models.DateTimeField(auto_now=True, null=True, db_column=b'grade_variacao_data_modificacao'),
        ),
    ]
