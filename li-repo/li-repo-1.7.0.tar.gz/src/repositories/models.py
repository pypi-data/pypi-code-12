# -*- coding: utf-8 -*-
from django.db import models
# from django.db.models.query import QuerySet
from unicodedata import normalize

# class PostMixin(object):
#     def get_object(self):
#         return { 'ok': 'ok!' }
#
# class PostQuerySet(QuerySet, PostMixin):
#     pass
#
# class MyObjects(models.Manager, PostMixin):
#
#     def get_query_set(self):
#         return PostQuerySet(self.model, using=self._db)

class MyObjects(models.Manager):
    pass

class Pais(models.Model):
    """Países."""
    id = models.CharField(db_column="pais_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="pais_nome", max_length=64)
    numero = models.CharField(db_column="pais_numero", max_length=3)
    codigo = models.CharField(db_column="pais_codigo", max_length=2, unique=True)

    objects = MyObjects()

    class Meta:
        app_label = "repositories_public"
        db_table = u"public\".\"tb_pais"


class Estado(models.Model):

    """Estados."""
    id = models.AutoField(db_column="estado_id", primary_key=True)
    uf_id = models.IntegerField(db_column="uf_id", unique=True)
    nome = models.CharField(db_column="estado_nome", max_length=100)
    uf = models.CharField(db_column="estado_uf", max_length=2)

    objects = MyObjects()

    pais = models.ForeignKey('repositories_public.Pais', db_column="pais_id")

    class Meta:
        app_label = "repositories_public"
        db_table = u"public\".\"tb_estado"


class Cidade(models.Model):

    """Cidades."""
    id = models.AutoField(db_column="cidade_id", primary_key=True)
    cidade = models.CharField(db_column="cidade", max_length=100)
    cidade_alt = models.CharField(db_column="cidade_alt", max_length=100)
    uf = models.CharField(db_column="uf", max_length=2)
    uf_munic = models.IntegerField(db_column="uf_munic")
    munic = models.IntegerField(db_column="munic")

    objects = MyObjects()

    estado = models.ForeignKey('repositories_public.Estado', db_column="uf_id")

    def get_object(self):
        dict = self.__dict__
        dict.pop("_django_version", None)
        dict.pop("_state", None)
        return dict

    class Meta:
        app_label = "repositories_public"
        db_table = u"public\".\"tb_cidade"


class Moeda(models.Model):

    """Moedas."""
    id = models.CharField(db_column="moeda_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="moeda_nome", max_length=64)

    objects = MyObjects()

    class Meta:
        app_label = "repositories_public"
        db_table = u"tb_moeda"


class Idioma(models.Model):

    """Idiomas."""
    id = models.CharField(db_column="idioma_id", max_length=5, primary_key=True)
    nome = models.CharField(db_column="idioma_nome", max_length=64)

    pais = models.ForeignKey('repositories_public.Pais', related_name="idiomas", default=None)

    objects = MyObjects()

    class Meta:
        app_label = "repositories_public"
        db_table = u"tb_idioma"


def remover_acentos(value):
    """Normalize the values."""
    try:
        return normalize('NFKD', value.decode('utf-8')).encode('ASCII', 'ignore')
    except UnicodeEncodeError:
        return normalize('NFKD', value).encode('ASCII', 'ignore')


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

    id = models.AutoField(db_column="imagem_id", primary_key=True)
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

    objects = MyObjects()

    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="imagens")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="imagens")

    class Meta:
        app_label = "repositories_public"
        db_table = u"plataforma\".\"tb_imagem"
        verbose_name = u"Imagem"
        verbose_name_plural = u"Imagens"
        ordering = ["data_criacao"]

    def __unicode__(self):
        return self.caminho

    @property
    def original(self):
        return self.caminho

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
