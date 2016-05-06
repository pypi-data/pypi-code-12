# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idioma',
            name='pais',
            field=models.ForeignKey(related_name='idiomas', default=None, blank=True, to='domain.Pais', null=True),
        ),
    ]
