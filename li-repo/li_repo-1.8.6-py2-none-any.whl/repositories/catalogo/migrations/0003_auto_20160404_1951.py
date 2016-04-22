# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='id_externo',
            field=models.IntegerField(default=None, null=True, db_column=b'grade_id_externo'),
        ),
    ]
