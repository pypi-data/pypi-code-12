# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0005_auto_20160414_1524'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='caracteristicavalor',
            options={'ordering': ['valor'], 'verbose_name': 'Valor da caracteristica', 'verbose_name_plural': 'Valores das caracteristicas'},
        ),
    ]
