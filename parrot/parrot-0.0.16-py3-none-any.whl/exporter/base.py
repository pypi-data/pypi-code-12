import logging
from parrot.utils import MethodsIfSilentIsDefinedMixin


logger = logging.getLogger(__name__)


class Exporter(MethodsIfSilentIsDefinedMixin):
    """
    Экспортирует (выводит) данные об объекте в определенном формате

    Например, выгружает собранные данные в формате csv
    """
    def __init__(
            self, init_export_func=None, item_export_func=None, *, silent=True
    ):
        """
        Функции init_export_func и item_export_func полезны в том случае, когда
        нужно выполнить определенные действия перед выгрузкой объектов.

        Например, init_export_func разбивает файлы по папкам, а
        item_export_func на основе результатов разбиения файлов заменяет старые
        пути к файлам на новые.

        Если не нужно выполнять никаких действий при инициализации или экспорте
        каждого объекта, то параметры init_export_func и item_export_func можно
        передать со значением None.

        :param init_export_func: функция, вызываем перед началом экспорта
                                 (вызывается один раз на вызов экспортера);
                                 не принимает аргументов
        :param item_export_func: функция, вызываемая перед экспортом каждого
                                 объекта; позволяет преобразовать объект перед
                                 выгрузкой; принимает первым аргументом всегда
                                 словарь или объект с поддержкой обращения по
                                 ключу, а вторым - результат вызова функции
                                 init_export_func; возващает только словарь;
        :param silent:
        :return:
        """
        self._init_export_func = init_export_func
        self._item_export_func = item_export_func
        self.silent = silent

    def _init_export(self):
        if self._init_export_func is None:
            return None
        return self._init_export_func()

    def _item_export(self, item, init):
        if self._item_export_func is None:
            return item
        return self._item_export_func(item, init)

    def __call__(self, items):
        """

        :param items: или итератор словарей, или итератор объектов, которые
                      после применения _item_export преобразуются в словари
        :return: total, success, error - кортеж из 3-х элементов
        """
        raise NotImplementedError(
            '{}.__call__ must be defined in child classes'.format(
                self.__class__.__name__
            )
        )
