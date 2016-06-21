# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0001_initial'),
        ('plataforma', '0001_initial'),
        ('cliente', '0001_initial'),
        ('catalogo', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientegrupo',
            name='conta',
            field=models.ForeignKey(related_name='grupos', blank=True, to='plataforma.Conta', null=True),
        ),
        migrations.AddField(
            model_name='clientegrupo',
            name='contrato',
            field=models.ForeignKey(related_name='grupos', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='clientefavoritoproduto',
            name='conta',
            field=models.ForeignKey(related_name='produtos_favoritos', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='clientefavoritoproduto',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_favoritos', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='clientefavoritoproduto',
            name='favorito',
            field=models.ForeignKey(related_name='produtos_favoritos', db_column=b'cliente_favorito_id', to='cliente.ClienteFavorito'),
        ),
        migrations.AddField(
            model_name='clientefavoritoproduto',
            name='produto',
            field=models.ForeignKey(related_name='produtos_favoritos', db_column=b'produto_id', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='clientefavorito',
            name='cliente',
            field=models.ForeignKey(to='cliente.Cliente', db_column=b'cliente_id'),
        ),
        migrations.AddField(
            model_name='clientefavorito',
            name='conta',
            field=models.ForeignKey(related_name='favoritos', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='clientefavorito',
            name='contrato',
            field=models.ForeignKey(related_name='favoritos', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='clientefavorito',
            name='produtos',
            field=models.ManyToManyField(related_name='favoritos', through='cliente.ClienteFavoritoProduto', db_column=b'produto_id', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='clienteendereco',
            name='cliente',
            field=models.ForeignKey(related_name='enderecos', to='cliente.Cliente'),
        ),
        migrations.AddField(
            model_name='clienteendereco',
            name='conta',
            field=models.ForeignKey(related_name='enderecos', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='clienteendereco',
            name='contrato',
            field=models.ForeignKey(related_name='enderecos', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='clienteendereco',
            name='pais',
            field=models.ForeignKey(related_name='enderecos', to='domain.Pais'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='conta',
            field=models.ForeignKey(related_name='clientes', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='contrato',
            field=models.ForeignKey(related_name='clientes', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='grupo',
            field=models.ForeignKey(related_name='clientes', db_column=b'cliente_grupo_id', to='cliente.ClienteGrupo'),
        ),
        migrations.AlterUniqueTogether(
            name='clientegrupo',
            unique_together=set([('conta', 'nome')]),
        ),
        migrations.AlterUniqueTogether(
            name='clienteendereco',
            unique_together=set([('tipo', 'cpf', 'rg', 'cnpj', 'razao_social', 'ie', 'nome', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'pais', 'cliente', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='cliente',
            unique_together=set([('conta', 'email')]),
        ),
    ]
