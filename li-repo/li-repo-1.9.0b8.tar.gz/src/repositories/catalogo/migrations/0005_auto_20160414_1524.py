# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0004_auto_20160405_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marca',
            name='nome',
            field=models.CharField(max_length=255, verbose_name=b'nome', db_column=b'marca_nome'),
        ),
    ]
