# -*- coding: utf-8 -*-
import uuid

from django.db import models
from repositories import custom_models
from repositories.libs import utils


LOGRADOUROS = {
    u'AEROPORTO': 'AER', u'ALAMEDA': 'AL', u'APARTAMENTO': 'AP',
    u'AVENIDA': 'AV', u'BECO': 'BC', u'BLOCO': 'BL', u'CAMINHO': 'CAM',
    u'ESCADINHA': 'ESCD', u'ESTAÇÃO': 'EST', u'ESTRADA': 'ETR',
    u'FAZENDA': 'FAZ', u'FORTALEZA': 'FORT', u'GALERIA': 'GL',
    u'LADEIRA': 'LD', u'LARGO': 'LGO', u'PRAÇA': 'PCA',
    u'PARQUE': 'PRQ', u'PRAIA': 'PR', u'QUADRA': 'QD',
    u'QUILÔMETRO': 'KM', u'QUINTA': 'QTA', u'RODOVIA': 'ROD',
    u'RUA': 'RUA', u'SUPER QUA': 'SQD', u'TRAVESSA': 'TRV',
    u'VIADUTO': 'VD', u'VILA': 'VL',
}


class Logradouro(models.Model):

    nome_local = models.CharField(db_column='nome_local', max_length=128, primary_key=True)
    uf = models.CharField(db_column="uf_log", max_length=2)
    cep_log = models.IntegerField(db_column="cep8_log")
    cep_ini = models.IntegerField(db_column="cep8_ini")
    cep_fim = models.IntegerField(db_column="cep8_fim")
    bairro = models.IntegerField(db_column="bairro")

    class Meta:
        db_table = u'tb_logradouro'


class Imagem(models.Model):
    """Imagens."""
    TIPO_LOGO = 'logo'
    TIPO_PRODUTO = 'produto'
    TIPO_BANNER = 'banner'
    TIPO_MARCA = 'marca'
    TIPO_UPLOAD = 'upload'
    TIPOS = [
        (TIPO_LOGO, u'Logo'),
        (TIPO_PRODUTO, u'Produto'),
        (TIPO_BANNER, u'Banner'),
        (TIPO_MARCA, u'Marca'),
        (TIPO_UPLOAD, u'Upload')
    ]

    id = custom_models.BigAutoField(db_column="imagem_id", primary_key=True)
    tabela = models.CharField(db_column="imagem_tabela", max_length=64, null=True)
    campo = models.CharField(db_column="imagem_campo", max_length=64, null=True)
    linha_id = models.IntegerField(db_column="imagem_linha_id", null=True)
    data_criacao = models.DateTimeField(db_column="imagem_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="imagem_data_modificacao", auto_now=True)

    nome = models.CharField(db_column="imagem_nome", max_length=255, null=True)
    alt = models.CharField(db_column="imagem_alt", max_length=512, null=True)
    title = models.CharField(db_column="imagem_title", max_length=512, null=True)
    mime = models.CharField(db_column="imagem_mime", max_length=256, null=True)

    caminho = models.CharField(db_column="imagem_caminho", max_length=255, null=True)

    tipo = models.CharField(db_column="imagem_tipo", max_length=32,
                            choices=TIPOS, default=u'produto')
    processada = models.BooleanField(db_column="imagem_processada", default=False)
    conta = models.ForeignKey("plataforma.Conta", related_name="imagens")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="imagens")

    class Meta:
        db_table = u"plataforma\".\"tb_imagem"
        verbose_name = u"Imagem"
        verbose_name_plural = u"Imagens"
        ordering = ["data_criacao"]

    def __unicode__(self):
        return self.caminho

    @property
    def original(self):
        return self.caminho

    def save(self, *args, **kwargs):
        # Para que o usuário não fique sem visualizar nada enquanto a imagem é
        # redimensionada, o caminho da imagem é definido como todos os outros
        # valores da imagem.

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        # if self.conta.apelido == self.conta.CONTA_TESTE_APELIDO:
        #     self.tipo = 'imagem_teste'

        super(Imagem, self).save(*args, **kwargs)

    def delete_from_s3(self):
        """Remove esta imagem do S3."""
        if self.caminho:
            utils.delete_from_s3(self.caminho)

    def delete(self, *args, **kwargs):

        if not self.caminho.startswith('0/%s/' % self.conta.CONTA_TESTE_ID):
            self.delete_from_s3()
        super(Imagem, self).delete(*args, **kwargs)

    @property
    def imagem(self):
        """Retorna True caso o tipo de arquivo seja imagem."""
        if not self.mime:
            return True
        return self.mime.startswith('image')

    @property
    def extensao(self):
        return self.caminho.split('.')[-1]

    @property
    def filename(self):
        return self.caminho.split('/')[-1]

    def tamanhos(self):
        lista_tamanhos = ['icone', 'grande', 'media', 'pequena']
        saida = {}
        for tamanho in lista_tamanhos:
            saida[tamanho] = getattr(self, tamanho, None)
        return saida


class Moeda(models.Model):

    """Moedas."""
    id = models.CharField(db_column="moeda_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="moeda_nome", max_length=64)

    class Meta:
        db_table = u"tb_moeda"
        verbose_name = u"Moeda"
        verbose_name_plural = u"Moedas"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Pais(models.Model):

    """Países."""
    id = models.CharField(db_column="pais_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="pais_nome", max_length=64)
    numero = models.CharField(db_column="pais_numero", max_length=3)
    codigo = models.CharField(db_column="pais_codigo", max_length=2, unique=True)

    class Meta:
        app_label = "domain"
        db_table = u"tb_pais"
        verbose_name = u"País"
        verbose_name_plural = u"Países"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Estado(models.Model):

    """Estados."""
    id = custom_models.BigAutoField(db_column="estado_id", primary_key=True)
    uf_id = models.IntegerField(db_column="uf_id", unique=True)
    nome = models.CharField(db_column="estado_nome", max_length=100)
    uf = models.CharField(db_column="estado_uf", max_length=2)

    pais = models.ForeignKey('domain.Pais', related_name="estados")

    class Meta:
        db_table = u"tb_estado"
        verbose_name = u"Estado"
        verbose_name_plural = u"Estados"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Cidade(models.Model):
    """Cidades."""
    id = custom_models.BigAutoField(db_column="cidade_id", primary_key=True)
    nome = models.CharField(db_column="cidade", max_length=100)
    nome_alt = models.CharField(db_column="cidade_alt", max_length=100)
    uf = models.CharField(db_column="uf", max_length=2)
    uf_munic = models.IntegerField(db_column="uf_munic")
    munic = models.IntegerField(db_column="munic")

    estado = models.ForeignKey('domain.Estado', db_column="uf_id", to_field="uf_id",
                               related_name="cidades")

    class Meta:
        db_table = u"tb_cidade"
        verbose_name = u"Cidade"
        verbose_name_plural = u"Cidades"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class Idioma(models.Model):

    """Idiomas."""
    id = models.CharField(db_column="idioma_id", max_length=5, primary_key=True)
    nome = models.CharField(db_column="idioma_nome", max_length=64)

    pais = models.ForeignKey('domain.Pais', related_name="idiomas", default=None)

    class Meta:
        db_table = u"tb_idioma"
        verbose_name = u"Idioma"
        verbose_name_plural = u"Idiomas"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class UUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64)
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        if add:
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)


class ApiAplicacao(models.Model):
    """Aplicação para conectar a API."""
    id = custom_models.BigAutoField(db_column="api_aplicacao_id", primary_key=True)
    chave = UUIDField(db_column="api_aplicacao_chave", unique=True)
    nome = models.CharField(db_column="api_aplicacao_nome", max_length=255)
    data_criacao = models.DateTimeField(db_column="api_aplicacao_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="api_aplicacao_data_modificacao", auto_now=True, null=True)

    class Meta:
        db_table = u"plataforma\".\"tb_api_aplicacao"
        verbose_name = u"Aplicação da API"
        verbose_name_plural = u"Aplicações da API"
        ordering = ["nome"]

    def __unicode__(self):
        return self.nome


class MyObjects(models.Manager):
    pass


def remover_acentos(value):
    """Normalize the values."""
    try:
        return normalize('NFKD', value.decode('utf-8')).encode('ASCII', 'ignore')
    except UnicodeEncodeError:
        return normalize('NFKD', value).encode('ASCII', 'ignore')
