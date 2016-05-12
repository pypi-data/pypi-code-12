# coding: utf-8
"""
Módulo com modelos comuns para diversos projetos
"""
import os
from PIL import Image
from django.contrib.gis.db import models
from django.db.models import get_model
from django.db.models.signals import post_save, post_delete
from comum.settings import DDD_PADRAO
from comum.choices import TIPO_LINHA_CHOICES, TIPO_LINHA_COMERCIAL
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import GenericForeignKey
from django.conf import settings
from django.utils.translation import ugettext as _


def import_method(method):
    """
    Imports a namespaced method, such as myproj.myapp.mymodule.method
    """

    parts = method.split(".")
    namespace = ".".join(parts[:-1])
    method_name = parts[-1]

    try:
        module = __import__(namespace, fromlist=[method_name])
        method = getattr(module, method_name)
        return method
    except ImportError as impEr:
        return None


class AtivoManager(models.Manager):

    def __init__(self):
        super(AtivoManager, self).__init__()

    def get_queryset(self):

        qs = super(AtivoManager, self).get_queryset()
        return qs.filter(ativo=True)

    def ativos(self):

        qs = super(AtivoManager, self).get_queryset()
        return qs.filter(ativo=True)

    def inativos(self):
        qs = super(AtivoManager, self).get_queryset()
        return qs.filter(ativo=False)

    def todos(self):

        qs = super(AtivoManager, self).get_queryset()
        return qs


class DataHoraCriacaoMixIn(models.Model):

    """
    Classe abstrata que representa um campo para data/hora da criação
    do objeto
    """

    data_hora_criacao = models.DateTimeField(verbose_name=_(u"Data/Hora Criação"),
                                             help_text=_(u"Data/Hora da criaçao do objeto."),
                                             editable=False,
                                             auto_now_add=True)

    class Meta:

        abstract = True


class DataHoraAtualizacaoMixIn(models.Model):

    """
    Classe abstrata que representa um campo para data/hora da ultima
    atualizacao do objeto
    """

    data_hora_atualizacao = models.DateTimeField(verbose_name=_(u"Data/Hora"),
                                                 help_text=_(u"Data/Hora da última atualização do objeto."),
                                                 editable=False,
                                                 auto_now=True)

    class Meta:

        abstract = True


class DominioMixIn(models.Model):

    """
    Classe abstrata que representa um domínio codificado
    """

    valor = models.CharField(max_length=128,
                             unique=True,
                             verbose_name=_(u"Valor"),
                             help_text=_(u"Valor utilizado para substituir o código no sistema. Exemplo: 'Asfalto' para 'AS'."))

    def __unicode__(self):
        return self.valor

    class Meta:

        abstract = True


class DominioPonderadoMixIn(DominioMixIn):

    """
    Classe abstrata que representa um domínio codificado, com peso para cada
    objeto
    """

    peso = models.PositiveIntegerField(verbose_name=_(u"Peso"),
                                       help_text=_(u"Peso para o objeto do domínio"),
                                       default=1)

    class Meta:

        abstract = True


class GeoAtivoManager(models.GeoManager, AtivoManager):

    """
    Classe manager para flag ativo geográfico.
    """

    pass


class AtivoMixIn(models.Model):

    """
    Classe abstrata para representar uma flag de ativo ou não
    """

    ativo = models.NullBooleanField(verbose_name=_(u"Ativo"),
                                    help_text=_(u"Objeto ativo?"))

    def ativar(self):
        self.ativo = True
        self.save()

    def deativar(self):
        self.ativo = False
        self.save()

    class Meta:

        abstract = True


class OperadoraTelefonia(models.Model):

    nome = models.CharField(max_length=32,
                            verbose_name=_(u"Nome"),
                            help_text=_(u"Nome da operadora"),
                            unique=True)

    codigo = models.PositiveIntegerField(verbose_name=_(u"Código"),
                                         help_text=_(u"Código da operadora de telefonia, exemplo: EMBRATEL: 21"),
                                         unique=True)

    def __unicode__(self):

        """
        Retorna a representação unicode da operadora
        """

        return "{0} ({1})".format(self.nome, self.codigo)


class TipoLogradouro(DominioMixIn,
                     DataHoraCriacaoMixIn,
                     DataHoraAtualizacaoMixIn):

    pass


class Endereco(models.Model):

    objeto = GenericForeignKey()

    object_id = models.PositiveIntegerField(verbose_name=_(u"Id do Objeto Relacionado"),
                                            null=True,
                                            blank=True)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=u"Content-Type",
                                     null=True,
                                     blank=True,
                                     editable=False)

    municipio = models.ForeignKey("municipios.Municipio",
                                  verbose_name=_(U"Município"))

    tipo_logradouro = models.ForeignKey(TipoLogradouro,
                                        related_name="enderecos",
                                        verbose_name=_(u"Tipo Logradouro"))

    nome_logradouro = models.CharField(max_length=128,
                                       verbose_name=_(u"Nome Logradouro"))

    numero = models.CharField(max_length=16,
                              verbose_name=_(u"Número"))

    complemento = models.CharField(max_length=128,
                                   verbose_name=_(u"Complemento"),
                                   null=True,
                                   blank=True)

    cep = models.CharField(max_length=8,
                           verbose_name=_(u"CEP"),
                           blank=True,
                           null=True)

    def __unicode__(self):
        if self.cep:
            return u"{tipo_logradouro} {nome_logradouro}, {numero} - {municipio} ({uf}) - CEP: {cep}".format(tipo_logradouro=self.tipo_logradouro.valor,
                                                                                                             nome_logradouro=self.nome_logradouro,
                                                                                                             numero=self.numero,
                                                                                                             municipio=self.municipio.nome,
                                                                                                             uf=self.municipio.uf_sigla,
                                                                                                             cep=self.cep)

        else:
            return u"{tipo_logradouro} {nome_logradouro}, {numero} - {municipio} ({uf})".format(tipo_logradouro=self.tipo_logradouro.valor,
                                                                                                nome_logradouro=self.nome_logradouro,
                                                                                                numero=self.numero,
                                                                                                municipio=self.municipio.nome,
                                                                                                uf=self.municipio.uf_sigla)


class Telefone(models.Model):

    """
    Modela um telefone
    """

    ddd = models.PositiveIntegerField(verbose_name=_(u"DDD"),
                                      help_text=_(u"Código de discagem direta."),
                                      default=DDD_PADRAO)

    telefone = models.CharField(max_length=15,
                                verbose_name=_(u"Telefone"),
                                help_text=_(u"Número do telefone"))

    ramal = models.PositiveIntegerField(null=True,
                                        blank=True)

    tipo_linha = models.CharField(max_length=1,
                                  choices=TIPO_LINHA_CHOICES,
                                  verbose_name=_(u"Tipo de Linha"),
                                  help_text=_(u"Tipo da linha, exemplo: 'residencial','comercial', etc."),
                                  default=TIPO_LINHA_COMERCIAL)

    operadora = models.ForeignKey(OperadoraTelefonia,
                                  verbose_name=_(u"Operadora"),
                                  help_text=_(u"Operadora que suporta este número."),
                                  null=True,
                                  blank=True)

    objeto = GenericForeignKey()

    # object id do gerador do processo
    object_id = models.PositiveIntegerField(verbose_name=_(u"Id do Objeto Relacionado"),
                                            null=True,
                                            blank=True)

    # content type
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=u"Content-Type",
                                     null=True,
                                     blank=True,
                                     editable=False)

    def __unicode__(self):

        """
        Retorna a represetação unicode de um telefone
        """
        return u"0{0}-{1} ({2})".format(self.ddd, self.telefone, self.operadora)


class Anexo(DataHoraCriacaoMixIn, DataHoraAtualizacaoMixIn):

    """
    Modelo genérico para anexos
    """

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=u"ContentType",
                                     null=True,
                                     blank=True,
                                     editable=False)

    object_id = models.PositiveIntegerField(verbose_name=_(u"Dono Anexo"),
                                            null=True,
                                            blank=True,
                                            editable=False)

    objeto = GenericForeignKey()

    nome = models.CharField(max_length=128,
                            verbose_name=_(u"Nome"),
                            help_text=_(u"Nome do anexo."))

    descricao = models.CharField(max_length=128,
                                 verbose_name=_(u"Descrição"),
                                 help_text=_(u"Descrição do anexo."),
                                 null=True,
                                 blank=True)

    arquivo = models.FileField(verbose_name=_(u"Arquivo"),
                               upload_to="anexos/",
                               help_text=_(u"Arquivo"))

    @property
    def tipo_arquivo(self):
        return self.file_name.split(".")[1]

    @property
    def nome_arquivo(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = _(u"Anexo")
        verbose_name_plural = _(u"Anexos")

    def get_available_name(self, name):
        return name

    def _save(self, name, content):
        if self.exists(name):
            # if the file exists, do not call the superclasses _save method
            return name
        # if the file is new, DO call it
        return super(MediaFileSystemStorage, self)._save(name, content)


class Fotografia(DataHoraCriacaoMixIn, DataHoraAtualizacaoMixIn):

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_(u"ContentType"),
                                     null=True,
                                     blank=True,
                                     editable=False)

    object_id = models.PositiveIntegerField(verbose_name=_(u"Dono Fotografia"),
                                            null=True,
                                            blank=True,
                                            editable=False)

    objeto = GenericForeignKey()

    nome = models.CharField(max_length=128,
                            verbose_name=_(u"Nome"),
                            help_text=_(u"Nome da fotografia."))

    descricao = models.CharField(max_length=128,
                                 verbose_name=_(u"Descrição"),
                                 help_text=_(u"Descrição da Fotografia."),
                                 null=True,
                                 blank=True)

    arquivo = models.ImageField(verbose_name=_(u"Arquivo"),
                                upload_to="fotografias/",
                                help_text=_(u"Fotografia"))

    def save(self, force_insert=False, force_update=False, using=None, thumbnail_dimensions=None):

        super(Fotografia, self).save(force_insert=force_insert, force_update=force_update, using=using)

        if thumbnail_dimensions is not None:
            im = Image.open(self.arquivo)
            im.thumbnail(thumbnail_dimensions, Image.ANTIALIAS)
            im.save(self.arquivo.path)

    @property
    def tipo_arquivo(self):
        return self.file_name.split(".")[1]

    @property
    def nome_arquivo(self):
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = _(u"Fotografia")
        verbose_name_plural = _(u"Fotografias")


class TipoEmail(DominioMixIn):
    pass


class Email(models.Model):

    object_id = models.PositiveIntegerField(verbose_name=_(u"Id do Objeto Relacionado"),
                                            null=True,
                                            blank=True)

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=u"Content-Type",
                                     null=True,
                                     blank=True,
                                     editable=False)

    objeto = GenericForeignKey()

    email = models.EmailField(max_length=200)

    tipoemail = models.ForeignKey(TipoEmail,
                                  verbose_name=_(u'Tipo Email'),
                                  related_name='emails')

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = _(u'Email')
        ordering = ["tipoemail", "email"]


class AppModelMixin(models.Model):

    """
    Este modelo tem em seus atributos dados para referenciar uma
    aplicação e um modelo django.
    """

    app = models.CharField(max_length=128,
                           verbose_name=_(u"Aplicação Django"),
                           help_text=_(u"Aplicação Django que contém o modelo em questão"))

    modelo = models.CharField(max_length=128,
                              verbose_name=_(u"Modelo Django"),
                              help_text=_(u"Modelo Django que será utilizado."))

    @property
    def validar_modelo(self):
        """
        Valida se o modelo é válido ou não.
        """
        try:
            modelo = get_model(self.app, self.modelo)
            if modelo is None:
                return False
            else:
                return True
        except Exception:
            # todo: qualificar a exceção que é lançada quando não achamos um modelo.
            return False

    @property
    def ref_modelo(self):
        """
        Retorna uma referência ao modelo Django.
        Caso o modelo não exista ou seja inválido, retorna None.
        todo: este método duplica uma chamada a get_model. Reduzir esta duplicação.
        """
        if self.validar_modelo:
            return get_model(self.app, self.modelo)
        else:
            return None

    class Meta:
        abstract = True


class ModelListener(AppModelMixin):
    """ Monitora mudanças nos models e dispara ações apropriadas """

    name = models.CharField(max_length=64,
                            verbose_name=_(u"Nome do monitorador"))

    active = models.BooleanField(verbose_name=_(u"Ativo?"),
                                 help_text=_(u"Este monitorador está ativo?"),
                                 default=True)

    post_save_handler = models.CharField(max_length=128,
                                         verbose_name=_(u"Monitorador de salvamento"),
                                         help_text=_(u"Método que vai ser disparado para o evento que salva o post. Caminho completo do método, ex: meu_projeto.meu_aplicativo.handlers.handle_post_save"))

    post_delete_handler = models.CharField(max_length=128,
                                           verbose_name=_(u"Monitorador de exclusão"),
                                           help_text=_(u"Método que vai ser disparado para o evento que apaga o post. Caminho completo do método, ex: meu_projeto.meu_aplicativo.handlers.handle_post_delete"))

    listen_post_save = models.BooleanField(verbose_name=_(u"Monitora salvamento?"),
                                           help_text=_(u"Determina se o modelo vai monitorar eventos de salvamento."),
                                           default=True)

    listen_post_delete = models.BooleanField(verbose_name=_(u"Monitora exclusão?"),
                                             help_text=_(u"Determina se o modelo vai monitorar eventos de exclusão."),
                                             default=True)

    auto_on = models.BooleanField(verbose_name=_(u"Início automático?"),
                                  default=False)

    @property
    def post_save_uid(self):
        """
        Retorna o UID de despache.
        Essa UID vai ser utilizada para registrar o sinal de salvamento.
        """
        return "%s-%s-%s-post-save" % (self.app, self.modelo, self.post_save_handler)

    @property
    def post_delete_uid(self):
        """
        Retorna o UID de despache.
        Essa UID vai ser utilizada para registrar o sinal de exclusão.
        """
        return "%s-%s-%s-post-delete" % (self.app, self.modelo, self.post_delete_handler)

    def _is_method_valid(self, method):
        """ Garante que o método utilizado é valido """
        try:
            function = import_method(method)

            if not function:
                return False

            return True
        except ImportError as impEr:
            return False

    def is_valid_listener(self):
        """
        Testa se o monitorador é válido.
        Isso significa que:
        1 - aplicativo e modelo existem
        2 - método pode ser importado
        3 - método tem a assinatura esperada
        """

        model = self.ref_modelo

        if not model:
            return False

        if self.post_save_handler and not self._is_method_valid(self.post_save_handler):
            return False

        if self.post_delete_handler and not self._is_method_valid(self.post_delete_handler):
            return False

        return True

    def _start_listening(self):
        """ Inicia o monitoramento no modelo registrado """

        if not self.active:
            return

        model = self.ref_modelo

        if not model:
            return

        # only register signals if we are listening!
        if self.listen_post_save:
            try:

                function = import_method(self.post_save_handler)

                if function is not None:
                    post_save.connect(function, sender=model, dispatch_uid=self.post_save_uid)

            except ImportError:
                pass

        # only register signals if we are listening!
        if self.listen_post_delete:

            try:

                function = import_method(self.post_delete_handler)

                if function is not None:
                    post_delete.connect(function, sender=model, dispatch_uid=self.post_delete_uid)

            except ImportError:
                pass

    def _stop_listening(self):
        """
        Para o monitoramento.
        O método tentará desconectar todos os monitoradores,
        independente do status (ligado/desligado)
        """

        model = self.ref_modelo

        if not model:
            return

        post_save.disconnect(None, sender=model, dispatch_uid=self.post_save_uid)
        post_delete.disconnect(None, sender=model, dispatch_uid=self.post_delete_uid)

    def __unicode__(self):
        return _(u"Monitorando: {app}.{modelo}").format(app=self.app, modelo=self.modelo)

    def save(self, *args, **kwargs):
        if self.auto_on:
            self._start_listening()

        super(ModelListener, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u"Monitorador de Modelo")
        verbose_name_plural = _(u"Monitoradores de Modelo")


class ModelListenerManager(models.Manager):

    def start_listeners(self):
        """
        Inicia todos os monitoradores ativos
        # todo: migrate to manager?
        """

        for listener in self.get_query_set().filter(active=True):
            listener._start_listening()

    def stop_listeners(self):
        """
        Para todos os monitoradores ativos
        # todo: migrate to manager?
        """
        for listener in self.get_query_set().filter(active=True):
            listener._stop_listening()
