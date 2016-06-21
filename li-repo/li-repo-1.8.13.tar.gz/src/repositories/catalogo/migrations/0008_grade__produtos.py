# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0007_auto_20160426_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='_produtos',
            field=models.ManyToManyField(related_name='_grades', through='catalogo.ProdutoGrade', to='catalogo.Produto'),
        ),
    ]
