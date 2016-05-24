import logging
from parrot.exceptions import SerializerSerializingException
from parrot.utils import MethodsIfSilentIsDefinedMixin, traceback_in_one_line


logger = logging.getLogger(__name__)


class Serializer(MethodsIfSilentIsDefinedMixin):
    """
    Преобразует результат парсинга в объект, который можно сохранить в
    хранилище (например, в БД)

    Сериализатор поддерживает работу с одним аргументом
    не последовательностью (т. е. когда передается только объект,
    полученный после парсинга) и с последовательностью из двух или четырех
    аргументов (т. е. когда передается ссылка на объект
    полученный после парсинга и он сам или, когда передается ссылка на объект
    полученный после парсинга, он сам, ссылка на категорию и она сама).

    Количество элементов последовательности (2 или 4) определяется в процессе
    разработки парсера, т. е. если не нужна иформация о категории (
    используется метод контроллера _find_and_parse_items_without_section_info),
    тогда обрабатываем 1 элемент или последовательность из 2-х элементов,
    иначе -- 1 элемент или последовательность из 4-х элементов.
    """
    def __init__(
        self, single_serialize_func=None, sequence_serialize_func=None, *,
        silent=True
    ):
        """
        :param single_serialize_func: функция, обрабатывающая одиночный элемент
        :param sequence_serialize_func: функция, обрабатывающая последовательности
        :param silent:
        :return:
        """
        self._single_serialize_func = single_serialize_func
        self._sequence_serialize_func = sequence_serialize_func
        self.silent = silent

    def _single_serialize(self, item):
        if self._single_serialize_func is None:
            raise NotImplementedError(
                '{}._single_serialize must be defined in child classes '
                'or passed as init parameter'.format(self.__class__.__name__)
            )
        return self._single_serialize_func(item)

    def _sequence_serialize(self, *item):
        if self._sequence_serialize_func is None:
            raise NotImplementedError(
                '{}._sequence_serialize must be defined in child classes '
                'or passed as init parameter'.format(self.__class__.__name__)
            )
        return self._sequence_serialize_func(*item)

    def _dispatch(self, item):
        if isinstance(item, (tuple, list)):
            return self._sequence_serialize(*item)
        return self._single_serialize(item)

    def __call__(self, item):
        """
        Преобразует объект в словарь, который потом можно передать в хранилище

        В тихом режиме в случае ошибки возвращает None.
        :param item:
        """
        try:
            serialized = self._dispatch(item)
        except Exception as exc:
            custom_exc = SerializerSerializingException(
                item, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc, logger)
            logger.warning(custom_exc)
            return
        return serialized
