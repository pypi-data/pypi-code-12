# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0008_grade__produtos'),
        ('domain', '0005_auto_20160427_1340'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cidade',
            options={'ordering': ['cidade'], 'verbose_name': 'Cidade', 'verbose_name_plural': 'Cidades'},
        ),
        migrations.RenameField(
            model_name='cidade',
            old_name='nome',
            new_name='cidade',
        ),
        migrations.RenameField(
            model_name='cidade',
            old_name='nome_alt',
            new_name='cidade_alt',
        ),
        migrations.AddField(
            model_name='imagem',
            name='_produtos',
            field=models.ManyToManyField(related_name='_produtos', through='catalogo.ProdutoImagem', to='catalogo.Produto'),
        ),
    ]
