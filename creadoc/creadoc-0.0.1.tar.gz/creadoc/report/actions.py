# coding: utf-8
from m3.actions import ActionPack


class CreadocDataSourceActionPack(ActionPack):
    u"""
    Пак для подвязывания источников данных,
    представляющих из себя обычные экшены
    """
    url = '/data'

    def add_action_in_runtime(self, action, attr_name=None):
        u"""
        Привязка действия к паку в рантайме.

        Из-за особенностей реализации логики привязки экшенов
        существует проблема, в связи с которой мы можем расширить
        список действий только уже после привязки пака к контроллеру
        и формирования ControllerCache. В связи с этим данный метод позволяет с
        крыть внутреннюю реализацию подвязывания экшена,
        однако на текущий момент использует защищенные методы.

        :param action: Экземпляр экшена
        :param attr_name: Наименование атрибута пака,
            под которым будет доступен инстанс экшена
        """
        if attr_name is not None:
            setattr(self, attr_name, action)

        self.actions.append(action)
        # Единственный приемлимый способ добавить экшен в рантайме
        self.controller._build_pack_node(action, [self])
