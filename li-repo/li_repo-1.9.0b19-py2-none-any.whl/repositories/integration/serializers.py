# -*- coding: utf-8 -*-
"""
Utiliza o conversor Modelo -> JSON genérico
para exportar os modelos.

Crie uma classe para cada modelo que deseja converter.
-   Em 'model' informe o modelo que será convertido
-   Em 'foreign_fields' informe os campos relacionais que devem ser convertidos
-   Em 'ignore_fields' informe os campos que deverão ser ignorados. O campo
    será ignorado na instancia enviada e nas subsinstâncias vindas dos campos
    relacionais.

PEP8: OK
"""
from . import integrations


class ProdutoSerializer(integrations.LISerializer):
    model = 'Produto'
    foreign_fields = [
        'imagens',
        'grades',
        'categorias',
        'categoria_global',
        'pai',
        'marca',
        'conta',
        'contrato'
    ]
    ignore_fields = [
        'certificado_ssl',
        'loja_layout'
    ]
