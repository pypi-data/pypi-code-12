# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0004_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idioma',
            name='pais',
            field=models.ForeignKey(related_name='idiomas', default=None, to='domain.Pais', null=True),
        ),
    ]
