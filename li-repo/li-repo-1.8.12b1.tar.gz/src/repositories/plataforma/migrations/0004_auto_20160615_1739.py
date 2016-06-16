# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0003_auto_20160426_2259'),
    ]

    operations = [
        migrations.CreateModel(
            name='EscopoPermissao',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'id')),
                ('nome', models.CharField(unique=True, max_length=100, verbose_name='Nome do escopo', db_column=b'nome_escopo')),
            ],
            options={
                'db_table': 'plataforma"."tb_escopo_permissao',
                'verbose_name': 'Escopo de permiss\xf5es',
            },
        ),
        migrations.CreateModel(
            name='GrupoPermissao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'id')),
                ('grupo_codigo', models.CharField(unique=True, max_length=100, verbose_name='Nome identificador do grupo', db_column=b'grupo_codigo')),
                ('nome_exibicao', models.CharField(max_length=100, verbose_name='Nome de exibi\xe7\xe3o do grupo', db_column=b'nome_exibicao')),
                ('descricao', models.CharField(max_length=255, null=True, verbose_name='Descri\xe7\xe3o do grupo', db_column=b'descricao_grupo')),
                ('padrao', models.BooleanField(default=False, verbose_name='Se o grupo \xe9 padr\xe3o para cria\xe7\xe3o de novos usu\xe1rios', db_column=b'padrao')),
                ('contrato', models.ForeignKey(related_name='grupo_permissao', to='plataforma.Contrato', null=True)),
            ],
            options={
                'db_table': 'plataforma"."tb_grupo_permissao',
                'verbose_name': 'Grupo de permiss\xf5es',
                'verbose_name_plural': 'Grupo de permiss\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Permissao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'id')),
                ('permitido', models.BooleanField(default=False, db_column=b'permitido')),
                ('escopo', models.ForeignKey(related_name='permissao', to='plataforma.EscopoPermissao')),
                ('grupo', models.ForeignKey(related_name='permissao', to='plataforma.GrupoPermissao')),
            ],
            options={
                'db_table': 'plataforma"."tb_permissao',
                'verbose_name': 'Permiss\xf5es',
            },
        ),
        migrations.RenameField(
            model_name='conta',
            old_name='nome_loja',
            new_name='nome',
        ),
        migrations.AddField(
            model_name='escopopermissao',
            name='grupo',
            field=models.ManyToManyField(related_name='escopo_permissao', to='plataforma.GrupoPermissao'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='grupo',
            field=models.ForeignKey(related_name='usuarios', to='plataforma.GrupoPermissao', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='permissao',
            unique_together=set([('escopo', 'grupo')]),
        ),
    ]
