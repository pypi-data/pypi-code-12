# -*- coding: utf-8 -*-
from repositories.integration.base import notifications
from repositories.catalogo.models import Produto, Marca
from repositories.integration.serializers import ProdutoSerializer, MarcaSerializer


class ProdutoNotifier(notifications.BaseNotificationService):

    model = Produto

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

    def model_to_dict(self):
        self.model_dict = ProdutoSerializer(self.instance).serialize()


class MarcaNotifier(notifications.BaseNotificationService):

    model = Marca

    def model_select_is_valid(self, obj):
        result = super(MarcaNotifier, self).model_select_is_valid(obj)
        if result:
            if obj.conta.id != self.account_id:
                raise ValueError(
                    u"A conta informada ({}) não é "
                    u"valida para esta Marca ({})".format(
                        obj.conta.id, self.account_id))
            return obj.ativo

    def model_to_dict(self):
        self.model_dict = MarcaSerializer(self.instance).serialize()
