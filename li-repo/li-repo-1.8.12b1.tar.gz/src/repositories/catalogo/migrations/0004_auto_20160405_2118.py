# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0003_auto_20160404_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradevariacao',
            name='id_externo',
            field=models.IntegerField(default=None, null=True, db_column=b'grade_variacao_id_externo'),
        ),
    ]
