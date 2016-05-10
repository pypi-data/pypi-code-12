# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0001_initial'),
        ('plataforma', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagem',
            name='conta',
            field=models.ForeignKey(related_name='imagens', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='imagem',
            name='contrato',
            field=models.ForeignKey(related_name='imagens', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='idioma',
            name='pais',
            field=models.ForeignKey(related_name='idiomas', default=None, to='domain.Pais'),
        ),
        migrations.AddField(
            model_name='estado',
            name='pais',
            field=models.ForeignKey(related_name='estados', to='domain.Pais'),
        ),
        migrations.AddField(
            model_name='cidade',
            name='estado',
            field=models.ForeignKey(related_name='cidades', db_column=b'uf_id', to_field=b'uf_id', to='domain.Estado'),
        ),
    ]
