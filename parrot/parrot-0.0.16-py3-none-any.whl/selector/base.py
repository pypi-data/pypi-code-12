import logging
from parrot.utils import MethodsIfSilentIsDefinedMixin


logger = logging.getLogger(__name__)


class Selector(MethodsIfSilentIsDefinedMixin):
    """
    Объект, осуществляющий выборку/поиск элементов во входящих данных,
    например, HTML-коде.

    Пример:
    selector = Selector()
    result = selector(data)
    """
    def __init__(self, *, silent=True):
        self.silent = silent

    def __call__(self, *pargs, **kwargs):
        raise NotImplementedError(
            '{}.__call__ must be defined in child classes'.format(
                self.__class__.__name__
            )
        )


class SingleSelector(Selector):
    """
    Селектор, возвращающий только одно (первое) найденное значение

    Должен указываться в списке базовых классов после класса, который реализует
    метод __call__.
    """
    def __call__(self, *pargs, **kwargs):
        candidates = super(self.__class__, self).__call__(*pargs, **kwargs)
        return candidates[0] if candidates else None


class MultiSelector(Selector):
    """
    Селектор, возвращающий все найденные значения

    Должен указываться в списке базовых классов после класса, который реализует
    метод __call__.
    """
    def __call__(self, *pargs, **kwargs):
        candidates = super(self.__class__, self).__call__(*pargs, **kwargs)
        return candidates or []


class FakeSelector(Selector):
    """
    Селектор, имитирующий поиск

    Полезен в ситуациях, когда нужно передать в форматтер весь data.
    """
    def __call__(self, data):
        return data
