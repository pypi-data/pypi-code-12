# -*- coding: utf-8 -*-
"""
LI-Repo.

Contém os modelos utilizados na Loja-Integrada

Attributes:
    IMPORT_STATUS (Lista): Status da Importação de Produtos, via excel

PEP8: OK
"""
from __future__ import print_function, unicode_literals

from ..models import MyObjects
from django.db import models
from jsonfield import JSONField

IMPORT_STATUS_RECEIVED = "received"
IMPORT_STATUS_PROCESSING = "processing"
IMPORT_STATUS_FAIL = "fail"
IMPORT_STATUS_PARTIAL = "partial"
IMPORT_STATUS_SUCCESS = "success"

IMPORT_STATUS = [
    (IMPORT_STATUS_RECEIVED, u"Arquivo recebido"),
    (IMPORT_STATUS_PROCESSING, u"Em processamento"),
    (IMPORT_STATUS_FAIL, u"Falha"),
    (IMPORT_STATUS_PARTIAL, u"Importado Parcialmente"),
    (IMPORT_STATUS_SUCCESS, u"Sucesso"),
]


LOG_IMPORT_CREATED = "created"
LOG_IMPORT_UPDATED = "updated"

LOG_IMPORT = [
    (LOG_IMPORT_CREATED, u"Produto criado"),
    (LOG_IMPORT_UPDATED, u"Produto atualizado"),
]


class Contrato(models.Model):

    id = models.AutoField(db_column="contrato_id", primary_key=True)
    nome = models.CharField(db_column="contrato_nome", max_length=255)
    ativo = models.BooleanField(db_column="contrato_ativo", default=True)
    codigo = models.CharField(
        db_column="contrato_codigo",
        max_length=255,
        unique=True)
    dominio = models.CharField(db_column="contrato_dominio", max_length=255)
    url_institucional = models.CharField(
        db_column="contrato_url_institucional",
        max_length=255)
    parametros = JSONField(
        u'Parametros do contrato',
        db_column="contrato_parametros",
        null=True)
    tipo = models.CharField(db_column="contrato_tipo", max_length=32)

    data_inicio = models.DateField(db_column='contrato_data_inicio')
    dia_vencimento = models.IntegerField(
        default=None,
        null=True,
        db_column='contrato_dia_vencimento',
        blank=True)

    minimo_mensal_valor = models.DecimalField(
        db_column="contrato_minimo_mensal_valor",
        max_digits=16,
        decimal_places=2,
        null=0.00)
    minimo_mensal_inicio_em_meses = models.IntegerField(
        db_column="contrato_minimo_mensal_inicio_em_meses",
        null=True,
        default=0)

    razao_social = models.CharField(
        db_column="contrato_razao_social",
        max_length=255)
    tipo_pessoa = models.CharField(
        db_column="contrato_tipo_pessoa",
        max_length=2,
        null=True,
        default='PJ')
    cpf_cnpj = models.CharField(
        db_column="contrato_cpf_cnpj",
        max_length=15,
        null=True,
        default=None)
    nome_responsavel = models.CharField(
        db_column="contrato_nome_responsavel",
        max_length=128,
        null=True,
        default=None)
    email_nota_fiscal = models.CharField(
        db_column="contrato_email_nota_fiscal",
        max_length=128,
        null=True,
        default=None)
    telefone_principal = models.CharField(
        db_column="contrato_telefone_principal",
        max_length=11,
        null=True,
        default=None)
    telefone_celular = models.CharField(
        db_column="contrato_telefone_celular",
        max_length=11,
        null=True,
        default=None)
    endereco_logradouro = models.CharField(
        db_column="contrato_endereco_logradouro",
        max_length=128,
        null=True,
        default=None)
    endereco_numero = models.CharField(
        db_column="contrato_endereco_numero",
        max_length=32,
        null=True,
        default=None)
    endereco_complemento = models.CharField(
        db_column="contrato_endereco_complemento",
        max_length=128,
        null=True,
        default=None)
    endereco_bairro = models.CharField(
        db_column="contrato_endereco_bairro",
        max_length=50,
        null=True,
        default=None)
    endereco_cep = models.CharField(
        db_column="contrato_endereco_cep",
        max_length=8,
        null=True,
        default=None)
    endereco_cidade_ibge = models.IntegerField(
        db_column="contrato_endereco_cidade_ibge",
        null=True,
        default=None)
    endereco_estado = models.CharField(
        u'Estado',
        db_column="contrato_endereco_estado",
        max_length=2,
        null=True,
        default=None)

    url_termo = models.TextField(
        db_column="contrato_url_termo",
        null=True,
        default=None)
    headtags = models.TextField(
        db_column="contrato_headtags",
        null=True,
        default=None)

    chave = models.CharField(db_column="contrato_chave")

    objects = MyObjects()

    colecao = models.ForeignKey(
        'repositories_faturamento.Colecao',
        db_column="colecao_id")

    def __str__(self):              # __unicode__ on Python 2
        return "%s the restaurant" % self.dominio

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_contrato"


class Conta(models.Model):

    CONTA_SITUACOES = [
        ('ATIVA', 'Loja ATIVA'),
        ('BLOQUEADA', 'Loja BLOQUEADA'),
        ('CANCELADA', 'Loja CANCELADA')
    ]

    id = models.AutoField(db_column="conta_id", primary_key=True)
    apelido = models.CharField(db_column="conta_apelido", max_length=32)
    nome = models.CharField(
        db_column="conta_loja_nome",
        max_length=128,
        null=False)
    email = models.CharField(
        db_column="conta_loja_email",
        max_length=128,
        null=True,
        default=None)
    dominio = models.CharField(
        db_column="conta_loja_dominio",
        max_length=128,
        null=True,
        default=None)
    situacao = models.CharField(
        db_column="conta_situacao",
        max_length=32,
        null=False,
        default='ATIVA',
        choices=CONTA_SITUACOES)
    modo = models.CharField(
        db_column="conta_loja_modo",
        max_length=32,
        null=False,
        default="loja")
    verificada = models.BooleanField(
        db_column="conta_verificada",
        default=False)

    logo = models.CharField(
        db_column="conta_logo",
        max_length=128,
        null=True,
        default=None)
    telefone = models.CharField(
        db_column="conta_loja_telefone",
        max_length=20,
        null=True,
        default=None)
    facebook = models.CharField(
        db_column="conta_loja_facebook",
        max_length=128,
        null=True,
        default=None)
    google_plus = models.CharField(
        db_column="conta_loja_google_plus",
        max_length=128,
        null=True,
        default=None)
    twitter = models.CharField(
        db_column="conta_loja_twitter",
        max_length=128,
        null=True,
        default=None)
    youtube = models.CharField(
        db_column="conta_loja_youtube",
        max_length=128,
        null=True,
        default=None)
    instagram = models.CharField(
        db_column="conta_loja_instagram",
        max_length=128,
        null=True,
        default=None)
    pinterest = models.CharField(
        db_column="conta_loja_pinterest",
        max_length=128,
        null=True,
        default=None)
    blog = models.URLField(
        db_column="conta_loja_blog",
        max_length=256,
        null=True)
    whatsapp = models.CharField(
        db_column="conta_loja_whatsapp",
        max_length=20,
        null=True,
        default=None)
    skype = models.CharField(
        db_column='conta_loja_skype',
        max_length=64,
        null=True,
        default=None)
    endereco = models.CharField(
        db_column="conta_loja_endereco",
        max_length=128,
        null=True,
        default=None)

    loja_manutencao = models.BooleanField(
        db_column="conta_loja_manutencao",
        default=False)

    habilitar_facebook = models.BooleanField(
        db_column='conta_habilitar_facebook',
        default=False)
    habilitar_mercadolivre = models.BooleanField(
        db_column='conta_habilitar_mercadolivre',
        default=False)
    habilitar_mobile = models.BooleanField(
        db_column='conta_habilitar_mobile',
        default=True)

    data_criacao = models.DateTimeField(
        db_column="conta_data_criacao",
        auto_now_add=True)
    data_modificacao = models.DateTimeField(
        db_column="conta_data_modificacao",
        auto_now=True,
        null=True)
    data_cancelamento = models.DateTimeField(
        db_column="conta_data_cancelamento",
        null=True)

    objects = MyObjects()

    contrato = models.ForeignKey(Contrato, db_column="contrato_id")
    plano = models.ForeignKey(
        'repositories_faturamento.Plano',
        db_column="plano_id")

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_conta"

    @property
    def url_dominio(self):
        if self.dominio:
            return self.dominio
        else:
            return self.url_subdominio

    @property
    def url_subdominio_facebook(self):
        return "%s-facebook.%s" % (self.apelido, self.contrato.dominio)

    @property
    def url_subdominio(self):
        return "%s.%s" % (self.apelido, self.contrato.dominio)

    @property
    def email_contato(self):
        if self.email:
            return self.email
        try:
            return self.usuarios.all()[0].email
        except IndexError:
            return None


class Dominio(models.Model):
    """Lista de domínios habilitados para uma conta."""
    id = models.AutoField(db_column="dominio_id", primary_key=True)
    fqdn = models.CharField(
        db_column="dominio_fqdn",
        max_length=128,
        null=False,
        unique=True)
    principal = models.BooleanField(
        db_column="dominio_principal",
        default=False,
        db_index=True)

    objects = MyObjects()

    conta = models.ForeignKey(
        Conta,
        db_column="conta_id",
        related_name="dominios")

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"configuracao\".\"tb_dominio"


class Usuario(models.Model):

    id = models.AutoField(db_column="usuario_id", primary_key=True)
    nome = models.CharField(db_column="usuario_nome", max_length=128)
    email = models.EmailField(db_column="usuario_email")
    confirmado = models.BooleanField(
        db_column="usuario_confirmado",
        default=False)

    objects = MyObjects()

    conta_id = models.ManyToManyField(
        Conta,
        related_name="usuarios",
        through="ContaUsuario")

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_usuario"

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]


class ContaUsuario(models.Model):
    """Relação entre conta e usuário."""
    id = models.AutoField(db_column="conta_usuario_id", primary_key=True)

    objects = MyObjects()

    usuario = models.ForeignKey(Usuario, db_column="usuario_id")
    conta = models.ForeignKey(Conta, db_column="conta_id")

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_conta_usuario"
        unique_together = ('conta', 'usuario')


class Certificado(models.Model):
    """Tipo de certificados a venda."""

    id = models.AutoField(db_column="certificado_id", primary_key=True)
    ativo = models.BooleanField(db_column="certificado_ativo", default=True)
    nome = models.CharField(db_column="certificado_nome", max_length=64)
    codigo = models.CharField(
        db_column="certificado_codigo",
        max_length=64,
        unique=True)
    fornecedor = models.CharField(
        db_column="certificado_fornecedor",
        max_length=128)
    fornecedor_site = models.CharField(
        db_column="certificado_fornecedor_site",
        max_length=256,
        null=True)
    descricao = models.TextField(
        db_column="certificado_descricao",
        null=True,
        default=None)
    valor = models.DecimalField(
        db_column="certificado_valor",
        max_digits=16,
        decimal_places=2)
    validade_anos = models.IntegerField(db_column="certificado_validade_anos")

    crt_intermediario = models.TextField(
        db_column="certificado_crt_intermediario",
        null=True)
    crt_raiz = models.TextField(db_column="certificado_crt_raiz", null=True)

    objects = MyObjects()

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_certificado"

    def __unicode__(self):
        return self.nome


class ContaCertificado(models.Model):
    """Gerencia os Certificados SSL instalados na Loja integrada."""

    id = models.AutoField(
        db_column="conta_certificado_id",
        primary_key=True,
        null=False)
    dominio = models.CharField(
        db_column="conta_certificado_dominio",
        max_length=128)
    key = models.TextField(db_column="conta_certificado_key", null=True)
    csr = models.TextField(db_column="conta_certificado_csr", null=True)
    crt = models.TextField(db_column="conta_certificado_crt", null=True)
    data_inicio = models.DateTimeField(
        db_column="conta_certificado_data_inicio",
        auto_now_add=True)
    data_expiracao = models.DateTimeField(
        db_column="conta_certificado_data_expiracao",
        null=True)
    situacao = models.CharField(
        db_column="conta_certificado_situacao",
        max_length=32)

    nc_compra_id = models.IntegerField(
        db_column="conta_certificado_namecheap_compra_id",
        null=True)
    nc_certificado_id = models.IntegerField(
        db_column="conta_certificado_namecheap_certificado_id",
        null=True)
    nc_transacao_id = models.IntegerField(
        db_column="conta_certificado_namecheap_transacao_id",
        null=True)

    confirmacoes = models.IntegerField(
        db_column="conta_certificado_confirmacoes",
        null=False,
        default=0)

    objects = MyObjects()

    certificado = models.ForeignKey(
        Certificado,
        related_name='contas',
        on_delete=models.CASCADE)
    contrato = models.ForeignKey(Contrato, db_column="contrato_id")
    conta = models.ForeignKey(Conta, db_column="conta_id")

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_conta_certificado"


class Imagem(models.Model):
    """Imagens."""

    id = models.AutoField(db_column="imagem_id", primary_key=True)
    tabela = models.CharField(
        db_column="imagem_tabela",
        max_length=64,
        null=True)
    campo = models.CharField(
        db_column="imagem_campo",
        max_length=64,
        null=True)
    linha_id = models.IntegerField(db_column="imagem_linha_id", null=True)
    data_criacao = models.DateTimeField(
        db_column="imagem_data_criacao",
        auto_now_add=True)
    data_modificacao = models.DateTimeField(
        db_column="imagem_data_modificacao",
        auto_now=True)

    caminho = models.CharField(db_column="imagem_caminho", null=True)

    tipo = models.CharField(db_column="imagem_tipo", max_length=32)
    processada = models.BooleanField(db_column="imagem_processada")

    objects = MyObjects()

    contrato = models.ForeignKey(Contrato, db_column="contrato_id")
    conta = models.ForeignKey(Conta, db_column="conta_id")

    produtos = models.ManyToManyField(
        'repositories_catalogo.Produto',
        through='repositories_catalogo.ProdutoImagem',
        related_name='produtos')

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_imagem"


class URL(models.Model):
    """URLs dos recursos do sistema.

    Define uma URL para um recurso da loja. Todas as URLs são únicas para a
    loja. Cada recurso deve ter pelo menos uma URL principal, caso não tenha,
    a URL mais nova é assumida como principal.
    """

    id = models.AutoField(db_column="url_id", primary_key=True)
    data_criacao = models.DateTimeField(
        db_column="url_data_criacao",
        auto_now_add=True)
    data_modificacao = models.DateTimeField(
        db_column="url_data_modificacao",
        auto_now=True)
    url = models.CharField(
        db_column="url_canonical_url",
        max_length=1024,
        null=False)
    principal = models.BooleanField(db_column="url_principal", default=True)

    produto = models.ForeignKey(
        "repositories_catalogo.Produto",
        related_name="urls",
        null=True,
        on_delete=models.CASCADE)
    categoria = models.ForeignKey(
        "repositories_catalogo.Categoria",
        related_name="urls",
        null=True,
        on_delete=models.CASCADE)
    # marca = models.ForeignKey(
    #       "repositories_catalogo.Marca",
    #       related_name="urls",
    #       null=True,
    #       on_delete=models.CASCADE
    #   )
    # pagina = models.ForeignKey(
    #       "repositories_plataforma.Pagina",
    #       related_name="urls",
    #       null=True,
    #       on_delete=models.CASCADE
    #   )

    conta = models.ForeignKey(
        "repositories_plataforma.Conta",
        related_name="urls")
    contrato = models.ForeignKey(
        "repositories_plataforma.Contrato",
        related_name="urls")

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_url"
#        unique_together = (("url", "conta", "contrato"),)


class ProductImportHistory(models.Model):
    """
    Classe ProductImportHistory.

    Para guardar o histórico de importações da Conta,
    através do arquivo excel modelo.
    """
    id = models.AutoField(
        db_column="historico_importacao_id",
        primary_key=True
    )
    account = models.ForeignKey(
        Conta,
        verbose_name='Conta',
        db_column="conta_id",
        help_text=u'Número da Loja'
    )

    contract = models.ForeignKey(
        Contrato,
        verbose_name='Contrato',
        db_column='contrato_id',
        help_text=u'Número do Contrato'
    )

    date_created = models.DateTimeField(
        db_column="historico_importacao_data_criacao",
        verbose_name=u'Data da Criação',
        auto_now_add=True,
        auto_now=False,
        help_text=u'Data da importação do arquivo'
    )

    date_start = models.DateTimeField(
        db_column="historico_importacao_data_inicio",
        verbose_name=u'Data de Início',
        help_text=u'Data do início da importação do arquivo',
        null=True,
        blank=True
    )

    date_end = models.DateTimeField(
        db_column="historico_importacao_data_final",
        verbose_name=u'Data da Finalização',
        help_text=u'Data da finalização da importação do arquivo',
        null=True,
        blank=True
    )

    status = models.TextField(
        db_column='historico_importacao_status',
        verbose_name=u'Status da Importação',
        choices=IMPORT_STATUS,
        default=IMPORT_STATUS_RECEIVED,
        help_text=u'O status da importação do arquivo. '
        u'"Falha" significa que nenhum Produto foi importado. '
        u'"Importação Parcial" significa que nem todos os produtos'
        u'do arquivo foram importados. "Sucesso" significa '
        u'que todos os produtos no arquivo foram importados.'
    )
    log = models.TextField(
        db_column='historico_importacao_mensagem',
        verbose_name=u'Log da importação',
        null=True,
        blank=True,
        help_text=u'Mensagem sobre o status da importação,'
    )
    error_file = models.TextField(
        db_column='historico_importacao_arquivo_erro',
        verbose_name=u'Arquivo com Erros',
        null=True,
        blank=True,
        help_text=u'Arquivo Excel contendo as linhas que não '
        u'foram importadas devido a erros.'
    )
    original_file = models.TextField(
        db_column='historico_importacao_arquivo_original',
        verbose_name=u'Arquivo Original',
        null=True,
        blank=True,
        help_text=u'Arquivo Excel enviado pela Loja.'
    )
    total_quantity = models.IntegerField(
        db_column='historico_importacao_quantidade_total',
        verbose_name=u'Linhas Excel',
        help_text=u'Total de Linhas no arquivo Excel enviado',
        null=True,
        blank=True,
    )
    success_quantity = models.IntegerField(
        db_column='historico_importacao_quantidade_sucesso',
        verbose_name=u'Linhas importadas',
        help_text=u'Linhas do Excel importadas com sucesso',
        null=True,
        blank=True,
    )
    error_quantity = models.IntegerField(
        db_column='historico_importacao_quantidade_erro',
        verbose_name=u'Linhas com Erro',
        help_text=u'Linhas do Excel com erros',
        null=True,
        blank=True,
    )

    def __unicode__(self):
        return "{}: {}".format(
            self.date_created.strftime("%c"),
            self.get_status_display()
        )

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_importacao_historico"
        verbose_name = u'Histórico das Importação',
        verbose_name_plural = u'Histórico das Importações',
        ordering = ['date_created']
        unique_together = ['account', 'contract', 'original_file']


class ProductImportRelation(models.Model):

    id = models.AutoField(
        db_column="produto_importacao_id",
        primary_key=True
    )
    account = models.ForeignKey(
        Conta,
        verbose_name='Conta',
        db_column="conta_id",
        help_text=u'Número da Loja'
    )

    importacao = models.ForeignKey(
        ProductImportHistory,
        db_column='historico_importacao_id',
        help_text=u'Importação que gerou/atualizou o Produto'
    )

    contract = models.ForeignKey(
        Contrato,
        verbose_name='Contrato',
        db_column='contrato_id',
        help_text=u'Número do Contrato'
    )

    product = models.ForeignKey(
        'repositories_catalogo.Produto',
        verbose_name='Produto',
        db_column='produto_id',
        help_text=u'Produto'
    )

    status = models.TextField(
        db_column='produto_importacao_status',
        verbose_name=u'Resultado da Importação',
        choices=LOG_IMPORT,
        default=LOG_IMPORT_CREATED,
    )

    class Meta:
        app_label = 'repositories_plataforma'
        db_table = u"plataforma\".\"tb_importacao_produto"
        verbose_name = u"Relação de Produto por Importacao"
        verbose_name_plural = u"Relação de Produtos por Importacao"

    def __unicode__(self):
        return "{}: {} ({})".format(
            self.importacao,
            self.product,
            self.status
        )
