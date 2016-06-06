# -*- coding: utf-8 -*-
from repositories.integration.base import notifications
from repositories.catalogo.models import Produto
from repositories.integration.serializers import ProdutoSerializer


class ProdutoNotifier(notifications.BaseNotificationService):

    model = Produto

    def model_select_is_valid(self, obj):
        result = super(ProdutoNotifier, self).model_select_is_valid(obj)
        if result:
            result = obj.ativo
        return result

    def model_to_dict(self):
        self.model_dict = ProdutoSerializer(self.instance).serialize()
