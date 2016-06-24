# -*- coding: utf-8 -*-
from repositories.integration.base import notifications
from repositories.catalogo.models import (Produto, Marca, Categoria,
                                          ProdutoImagem, ProdutoGradeVariacao)
from repositories.integration.serializers import (
    ProdutoSerializer, MarcaSerializer, CategoriaSerializer,
    ProdutoImagemSerializer, ProdutoVariacaoSerializer
)


class ProdutoNotifier(notifications.BaseNotificationService):

    model = Produto
    serializer = ProdutoSerializer

    def model_select_is_valid(self, obj):
        result = super(ProdutoNotifier, self).model_select_is_valid(obj)
        if result:
            if obj.conta.id != self.account_id:
                raise ValueError(
                    u"A conta informada ({}) não é "
                    u"valida para este Produto ({})".format(
                        obj.conta.id, self.account_id))
            result = obj.ativo
        return result


class MarcaNotifier(notifications.BaseNotificationService):

    model = Marca
    serializer = MarcaSerializer

    def model_select_is_valid(self, obj):
        result = super(MarcaNotifier, self).model_select_is_valid(obj)
        if result:
            if obj.conta.id != self.account_id:
                raise ValueError(
                    u"A conta informada ({}) não é "
                    u"valida para esta Marca ({})".format(
                        obj.conta.id, self.account_id))
            return obj.ativo


class CategoriaNotifier(notifications.BaseNotificationService):

    model = Categoria
    serializer = CategoriaSerializer

    def model_select_is_valid(self, obj):
        result = super(CategoriaNotifier, self).model_select_is_valid(obj)
        if result:
            if obj.conta.id != self.account_id:
                raise ValueError(
                    u"A conta informada ({}) não é "
                    u"valida para esta Categoria ({})".format(
                        obj.conta.id, self.account_id))
            return obj.ativa


class ProdutoImagemNotifier(notifications.BaseNotificationService):

    model = ProdutoImagem
    serializer = ProdutoImagemSerializer

    def model_select_is_valid(self, obj):
        result = super(ProdutoImagemNotifier, self).model_select_is_valid(obj)
        if result:
            if obj.conta.id != self.account_id:
                raise ValueError(
                    u"A conta informada ({}) não é "
                    u"valida para esta Imagem ({})".format(
                        obj.conta.id, self.account_id))
            return obj.produto.ativo


class ProdutoVariacaoNotifier(notifications.BaseNotificationService):

    model = ProdutoGradeVariacao
    serializer = ProdutoVariacaoSerializer

    def model_select_is_valid(self, obj):
        result = super(
            ProdutoVariacaoNotifier,
            self).model_select_is_valid(obj)
        if result:
            if obj.conta.id != self.account_id:
                raise ValueError(
                    u"A conta informada ({}) não é "
                    u"valida para esta Variação ({})".format(
                        obj.conta.id, self.account_id))
            return obj.produto_pai.ativo
