# -*- coding: utf-8 -*-

from ..models import MyObjects, remover_acentos, Imagem
from ..marketing.models import SEO
from ..plataforma.models import URL

from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

class Produto(models.Model):
    TIPO_NORMAL = 'normal'
    TIPO_ATRIBUTO = 'atributo'
    TIPO_VIRTUAL = 'virtual'
    TIPO_OPCAO = 'atributo_opcao'
    TIPO_KIT = 'kit'

    CHOICES_PRODUTO_TIPOS = [
        (TIPO_NORMAL, u'Produto simples'),
        (TIPO_ATRIBUTO, u'Produto com opções'),
        (TIPO_VIRTUAL, u'Produto virtual'),
        (TIPO_OPCAO, u'Opção'),
        (TIPO_KIT, u'Kit de produtos')
    ]

    id = models.AutoField(db_column='produto_id', primary_key=True)
    id_externo = models.IntegerField(db_column="produto_id_externo", null=True)

    apelido = models.CharField(db_column='produto_apelido', max_length=255, default=None, null=True)
    modelo = models.CharField(db_column='produto_modelo', max_length=255, null=True, default=None)
    sku = models.CharField(db_column='produto_sku', max_length=255, null=True, default=None)
    ncm = models.CharField(db_column='produto_ncm', max_length=10, null=True, default=None)
    gtin = models.CharField(db_column='produto_gtin', max_length=14, null=True, default=None)
    ativo = models.BooleanField(db_column='produto_ativo', default=False)
    removido = models.BooleanField(db_column='produto_removido', default=False)
    peso = models.DecimalField(db_column='produto_peso', max_digits=16, decimal_places=3, default=None, null=True)
    altura = models.IntegerField(db_column='produto_altura', default=None, null=True)
    largura = models.IntegerField(db_column='produto_largura', default=None, null=True)
    profundidade = models.IntegerField(db_column='produto_comprimento', default=None, null=True)
    # template = models.CharField(db_column='produto_template', max_length=255, null=True, default=None)
    tipo = models.CharField(db_column='produto_tipo', max_length=255, null=True)
    bloqueado = models.BooleanField(db_column='produto_bloqueado', default=False, null=False)
    usado = models.BooleanField(db_column='produto_usado', default=False, null=False)

    nome = models.CharField(db_column='produto_nome', max_length=255, default=None, null=True)
    url_video_youtube = models.CharField(db_column='produto_url_video_youtube', max_length=255, default=None, null=True)
    descricao_completa = models.TextField(db_column='produto_descricao_completa', default=None, null=True)

    imagens = models.ManyToManyField('repositories_plataforma.Imagem', through='ProdutoImagem', related_name='produtos')
    grades = models.ManyToManyField('repositories_catalogo.Grade', through='ProdutoGrade', related_name='produtos')
    categorias = models.ManyToManyField('repositories_catalogo.Categoria', through='ProdutoCategoria', related_name='produtos')
    destaque = models.BooleanField(db_column='produto_destaque', null=False, default=False)

    objects = MyObjects()

    pai = models.ForeignKey('repositories_catalogo.Produto', db_column='produto_id_pai', null=True)
    marca = models.ForeignKey('repositories_catalogo.Marca', null=True)
    conta = models.ForeignKey('repositories_plataforma.Conta')
    contrato = models.ForeignKey('repositories_plataforma.Contrato')

    data_criacao = models.DateTimeField(db_column='produto_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='produto_data_modificacao', null=True, auto_now=True)

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_produto"
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        unique_together = (("conta", "sku"),)
        get_latest_by = 'id'

    def get_absolute_url(self, usa_dominio=True):
        if self.cache_url:
            if usa_dominio:
                return "http://{}{}".format(self.conta.url_dominio, self.cache_url)
            return self.cache_url
        return None


class Categoria(MPTTModel):
    id = models.AutoField(db_column="categoria_id", primary_key=True)
    id_externo = models.IntegerField(db_column="categoria_id_externo", null=True)

    ativa = models.BooleanField(db_column="categoria_ativa", default=True)
    # quantidade_filhos = models.IntegerField(db_column="categoria_filhos", default=0)
    url = models.CharField(db_column="categoria_url", null=True, max_length=255)

    nome = models.CharField(db_column='categoria_nome', max_length=255)
    descricao = models.TextField(db_column='categoria_descricao', null=True)

    posicao = models.IntegerField(db_column="categoria_posicao", default=0)
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.PROTECT)
    conta = models.ForeignKey('repositories_plataforma.Conta', db_column="conta_id")
    contrato = models.ForeignKey('repositories_plataforma.Contrato', db_column='contrato_id')

    data_criacao = models.DateTimeField(db_column="categoria_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="categoria_data_modificacao", auto_now=True)

    # objects = MyObjects()

    # pai = models.ForeignKey("self", db_column="categoria_id_pai", null=True, blank=True, related_name="filhos")
    # nivel_1 = models.ForeignKey("self", db_column="categoria_id_nivel_1", null=True, blank=True, related_name="filhos_nivel_1")
    # nivel_2 = models.ForeignKey("self", db_column="categoria_id_nivel_2", null=True, blank=True, related_name="filhos_nivel_2")
    # nivel_3 = models.ForeignKey("self", db_column="categoria_id_nivel_3", null=True, blank=True, related_name="filhos_nivel_3")

    produtos = models.ManyToManyField(Produto, through='repositories_catalogo.ProdutoCategoria', related_name='produtos')

    class MPTTMeta:
        order_insertion_by = ['posicao']
        master_tree = 'conta_id'


    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_categoria"


class ProdutoCategoria(models.Model):
    """Relação entre produto e categoria."""
    id = models.AutoField(db_column='produto_categoria_id', primary_key=True)
    principal = models.BooleanField(db_column='produto_categoria_principal', default=False)

    objects = MyObjects()

    produto = models.ForeignKey(Produto, db_column='produto_id', related_name='produto_categorias', on_delete=models.CASCADE)
    categoria = models.ForeignKey('repositories_catalogo.Categoria', related_name='produtos_categoria', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='produtos_categorias')
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name='produtos_categorias')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_produto_categoria"


class ProdutoImagem(models.Model):
    """Imagens de um produto."""
    id = models.AutoField(db_column='produto_imagem_id', primary_key=True)
    posicao = models.IntegerField(db_column='produto_imagem_posicao', null=True, default=None)
    principal = models.NullBooleanField(db_column='produto_imagem_principal', null=True, default=False)

    objects = MyObjects()

    # Os related_name's são "produto_imagens" e "produtos_imagem" pois já existe
    # "imagens" e "produtos" dentro do produto e imagens, respectivamente,
    # referenciando ao ManyToMany de Produto x Imagem.
    produto = models.ForeignKey(Produto, db_column='produto_id', related_name='produto_imagens', on_delete=models.CASCADE)
    imagem = models.ForeignKey(Imagem, related_name='produtos_imagem', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='produtos_imagens')
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name='produtos_imagens')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u'catalogo\".\"tb_produto_imagem'
        verbose_name = u'Imagem do produto'
        verbose_name_plural = u'Imagens dos produtos'
        ordering = ['produto', '-principal', 'posicao', 'id']


class ProdutoEstoque(models.Model):
    """Estoque de um produto."""
    SITUACAO_INDISPONIVEL = -1
    SITUACAO_DISPONIVEL = 0

    SITUACOES = [
        (SITUACAO_INDISPONIVEL, u'Indiponível'),
        (SITUACAO_DISPONIVEL, u'Diponível'),
    ]

    id = models.AutoField(db_column='produto_estoque_id', primary_key=True)
    gerenciado = models.BooleanField(db_column='produto_estoque_gerenciado', default=False)
    quantidade = models.DecimalField(db_column='produto_estoque_quantidade', max_digits=16, decimal_places=4, default=0)
    situacao_em_estoque = models.IntegerField(db_column='produto_estoque_situacao_em_estoque', default=0)
    situacao_sem_estoque = models.IntegerField(db_column='produto_estoque_situacao_sem_estoque', default=0)

    objects = MyObjects()

    produto = models.OneToOneField('repositories_catalogo.Produto', related_name='estoque', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='produtos_estoque')
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name='produtos_estoques')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_produto_estoque"
        verbose_name = u'Estoque do Produto'
        verbose_name_plural = u"Estoque dos Produtos"
        ordering = ['id']

    # TODO: Verificar se é usado em algum lugar, senao remover. unattis
    def incrementar(self, quantidade=None, motivo=None):
        """Adiciona a quantidade passada a quantidade de itens no estoque."""
        self.quantidade = self.quantidade + quantidade
        self.save()

    # TODO: Verificar se é usado em algum lugar, senao remover. unattis
    def reduzir(self, quantidade=None, motivo=None, pedido_venda=None):
        """Reduz a quantidade de itens no estoque. Caso o pedido_venda seja
        enviado, a quantidade é descartada e o pedido_venda será usado para
        identificar a quantidade a ser reduzida.
        """
        if pedido_venda:
            pedido_item = pedido_venda.itens.get(produto=self.produto)
            quantidade = pedido_item.quantidade

        self.quantidade = self.quantidade - quantidade
        self.save()


class ProdutoPreco(models.Model):
    """Preço de um produto."""
    id = models.AutoField(db_column='produto_preco_id', primary_key=True)
    cheio = models.DecimalField(db_column='produto_preco_cheio', max_digits=16, decimal_places=4, null=True)
    promocional = models.DecimalField(db_column='produto_preco_promocional', max_digits=16, decimal_places=4, null=True)
    custo = models.DecimalField(db_column='produto_preco_custo', max_digits=16, decimal_places=4, null=True)
    sob_consulta = models.BooleanField(db_column='produto_preco_sob_consulta', default=False)

    moeda = models.ForeignKey('repositories_public.Moeda', related_name='produtos_preco', default='BRL')
    produto = models.OneToOneField('repositories_catalogo.Produto', related_name='preco', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='produtos_preco')
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name='produtos_preco')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u'catalogo\".\"tb_produto_preco'
        verbose_name = u'Preço do produto'
        verbose_name_plural = u'Preços dos Produtos'
        ordering = ['id']


class ProdutoGrade(models.Model):
    """Relação entre produto e grade."""
    id = models.AutoField(db_column='produto_grade_id', primary_key=True)
    posicao = models.IntegerField(db_column='produto_grade_posicao', default=0)

    produto = models.ForeignKey(Produto, db_column='produto_id', related_name='produto_grades', on_delete=models.CASCADE)
    grade = models.ForeignKey('repositories_catalogo.Grade', related_name='produtos_grade', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='produtos_grades')
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name='produtos_grades')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_produto_grade"
        verbose_name = u'Grade de um produto'
        verbose_name_plural = u"Grades dos produtos"
        ordering = ['produto', 'grade']


class ProdutoGradeVariacao(models.Model):
    """Relação entre produto e as variações da grade."""
    id = models.AutoField(db_column='produto_grade_variacao_id', primary_key=True)
    produto = models.ForeignKey('repositories_catalogo.Produto', related_name='produto_grades_variacoes', on_delete=models.CASCADE)
    produto_pai = models.ForeignKey('repositories_catalogo.Produto', db_column='produto_id_pai', related_name='produto_grades_variacoes_filhos', on_delete=models.CASCADE)
    produto_grade = models.ForeignKey('repositories_catalogo.ProdutoGrade', related_name='produto_grades_variacoes', on_delete=models.CASCADE)
    grade = models.ForeignKey('repositories_catalogo.Grade', related_name='produtos_grade_variacoes', on_delete=models.CASCADE)
    variacao = models.ForeignKey('repositories_catalogo.GradeVariacao', db_column="grade_variacao_id", related_name='produtos_grade_variacoes', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='produtos_grades_variacoes')
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name='produtos_grades_variacoes')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_produto_grade_variacao"
        verbose_name = u'Variação da grade de um produto'
        verbose_name_plural = u"Variações das grades dos produtos"


class Grade(models.Model):
    """Grade para uma veriação de produtos."""
    id = models.AutoField(db_column='grade_id', primary_key=True)
    id_externo = models.IntegerField(db_column='grade_id_externo')
    nome = models.CharField(db_column='grade_nome', max_length=255)
    nome_visivel = models.CharField(db_column='grade_nome_visivel', max_length=255)
    data_criacao = models.DateTimeField(db_column='grade_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='grade_data_modificacao', auto_now=True)
    pode_ter_imagens = models.BooleanField(db_column="grade_pode_ter_imagens", null=False, default=False)
    tipo = models.CharField(db_column="grade_tipo", default="normal", max_length=32, null=False)
    posicao = models.IntegerField(db_column="grade_posicao", null=None, default=1000)

    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='grades', on_delete=models.CASCADE, null=True)
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name="grades")

    produtos = models.ManyToManyField('repositories_catalogo.Produto', through='repositories_catalogo.ProdutoGrade', related_name='produtos')

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_grade"
        verbose_name = u'Grade'
        verbose_name_plural = u'Grades'
        unique_together = (("conta", "nome"),)


class GradeVariacao(models.Model):
    """Variações de uma grade."""
    id = models.AutoField(db_column='grade_variacao_id', primary_key=True)
    id_externo = models.IntegerField(db_column='grade_variacao_id_externo')
    nome = models.CharField(db_column='grade_variacao_nome', max_length=255)
    data_criacao = models.DateTimeField(db_column='grade_variacao_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='grade_variacao_data_modificacao', auto_now=True)
    posicao = models.IntegerField(db_column='grade_variacao_posicao', null=True, default=0)
    cor = models.CharField(db_column="grade_variacao_cor", null=True, default=None, max_length=32)
    cor_secundaria = models.CharField(db_column="grade_variacao_cor_secundaria", null=True, default=None, max_length=32)

    grade = models.ForeignKey('repositories_catalogo.Grade', related_name='variacoes', on_delete=models.CASCADE)
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='variacoes', null=True)
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name="variacoes")

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_grade_variacao"
        verbose_name = u'Variação da grade'
        verbose_name_plural = u'Variações de grade'
        ordering = ['posicao', 'nome']
        unique_together = (("conta", "grade", "nome"),)


class Marca(models.Model):
    """Marca."""
    id = models.AutoField(db_column='marca_id', primary_key=True)
    id_externo = models.IntegerField(db_column="marca_id_externo", null=True)

    ativo = models.BooleanField(db_column='marca_ativo', default=False)
    destaque = models.BooleanField(db_column="marca_destaque", default=False, null=False)
    imagem = models.CharField(db_column="marca_imagem_caminho", null=True, blank=True, max_length=256)
    nome = models.CharField(db_column='marca_nome', max_length=255)
    apelido = models.CharField(db_column='marca_apelido', max_length=255, null=True)
    descricao = models.TextField(db_column='marca_descricao', null=True)

    objects = MyObjects()

    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='marcas', on_delete=models.CASCADE)
    contrato = models.ForeignKey('repositories_plataforma.Contrato', related_name="marcas")

    data_criacao = models.DateTimeField(db_column='marca_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='marca_data_modificacao', auto_now=True)

    class Meta:
        app_label = "repositories_catalogo"
        db_table = u"catalogo\".\"tb_marca"
        verbose_name = u'Marca'
        verbose_name_plural = u'Marcas'
        ordering = ['id']
        get_latest_by = 'id'


# # # TODOS OS POSTS SAVE FORAM ADICONADOS DAQUI PARA BAIXO!

@receiver(post_save, sender=Produto)
def produto_post_save(sender, instance, created, raw, **kwargs):

    # Cria as relações que o produto precisa para funcionar.
    if created and not getattr(instance, '_copia', False):

        # Estoque e preco somente para produto de fato
        # tipo 'atributo' nao deve ter preco e estoque. Adicionado para manter retrocompatili
        if instance.tipo in ('normal','atributo','atributo_opcao'):

            ProdutoEstoque.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id, produto_id=instance.id)

            ProdutoPreco.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id, produto_id=instance.id)

        # SEO para produto prinicpal ou atributo que agrupa as opcoes disponíveis
        if instance.tipo in ('normal', 'atributo'):

            SEO.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id,
                linha_id=instance.id, tabela='tb_produto')

            # Slufigy da URL
            url_slugify = '/' + slugify(u'{}-{}'.format(remover_acentos(instance.nome),instance.id))

            URL.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id, produto_id=instance.id,
                principal=True, url=url_slugify
            )


@receiver(post_save, sender=ProdutoCategoria)
def produto_categoria_post_save(sender, instance, created, raw, **kwargs):

    if instance.principal is True:

        total = ProdutoCategoria.objects.filter(
            ~Q(categoria_id=instance.categoria_id), produto_id=instance.produto_id, principal=True).count()

        # Se tem outra categoria como principal e esta esta para ser, desmarcar a anterior
        if total > 0:
            ProdutoCategoria.objects.filter(
                ~Q(categoria_id=instance.categoria_id), produto_id=instance.produto_id, principal=True).\
                update(principal=False)


@receiver(post_save, sender=Categoria)
def categoria_post_save(sender, instance, created, raw, **kwargs):

    if created:

        SEO.objects.create(
            contrato_id=instance.contrato_id, conta_id=instance.conta_id, linha_id=instance.id, tabela='tb_categoria')

        # Slufigy da URL
        url_slugify = '/' + slugify(u'{}-{}'.format(remover_acentos(instance.nome),instance.id))

        URL.objects.create(
            contrato_id=instance.contrato_id, conta_id=instance.conta_id, categoria_id=instance.id,
            principal=True, url=url_slugify
        )

# Caso apelido nao seja passado, cria.
# Este recurso pode ser eliminado após iniciar o uso da tabela de URL
@receiver(post_save, sender=Marca)
def marca_post_save(sender, instance, created, raw, **kwargs):

    # Cria as relações que o produto precisa para funcionar.
    if created and instance.apelido is None:

        # Slufigy da URL
        url_slugify = slugify('{}-{}'.format(remover_acentos(instance.nome),instance.id))

        instance.apelido = url_slugify
        instance.save()
