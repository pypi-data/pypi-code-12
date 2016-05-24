import logging
from parrot.exceptions import (
    InvalidData, InvalidValue, ParserFetchingDataException,
    InvalidDataFromSource, InvalidValueFromSource
)
from parrot.utils import MethodsIfSilentIsDefinedMixin, traceback_in_one_line


logger = logging.getLogger(__name__)


DEFAULT_ENCODING = 'utf-8'
DEFAULT_CODING_ERRORS = 'strict'


class Parser(MethodsIfSilentIsDefinedMixin):
    def __init__(
        self, handlers, loader, *,
        encoding=DEFAULT_ENCODING, coding_errors=DEFAULT_CODING_ERRORS,
        silent=True
    ):
        """
        :param handlers: словарь обработчиков {name: (selector, formatter)}
        :param encoding: кодировка результата _fetch_data
                         (не декодировать байты в строку, если None)
        :param coding_errors: режим обработки ошибки при
                              кодировании/декодировании строк/байт
                              (encode/decode);
                              передается в соответствующий метод без изменения;
                              допустимые значения и описания смотри в docstring
                              str.encode, bytes.decode
        :return:
        """
        self.handlers = handlers
        self.loader = loader
        self.encoding = encoding
        self.coding_errors = coding_errors
        self.silent = silent

    @classmethod
    def result_contain_attr(cls, result, attr):
        return isinstance(result, dict) and attr in result

    @classmethod
    def _is_valid_data(cls, data):
        return bool(data)

    def _validate_data(self, data, source=None):
        if not self._is_valid_data(data):
            exc = (
                InvalidData(data) if source is None
                else InvalidDataFromSource(data, source)
            )
            self._raise_if_not_silent(exc, logger)
            logger.warning(exc)
            return None
        return data

    @classmethod
    def _is_empty_value(cls, val):
        return not bool(val)

    @classmethod
    def _is_valid_value(cls, val):
        return not cls._is_empty_value(val)

    def _validate_value(self, val, source):
        if not self._is_valid_value(val):
            exc = (
                InvalidValue(val) if source is None
                else InvalidValueFromSource(val, source)
            )
            self._raise_if_not_silent(exc, logger)
            logger.warning(exc)
            return None
        return val

    def _fetch_data(self, source):
        try:
            data = self.loader(source)
            if data is None or self.encoding is None or isinstance(data, str):
                return data
            return data.decode(self.encoding, errors=self.coding_errors)
        except Exception as exc:
            custom_exc = ParserFetchingDataException(
                source, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc, logger)
            logger.error(custom_exc)
            return None

    def _parse_data(self, data, source=None):
        """
        Всегда должен возвращать словарь или None

        :param source: источник данных, например, ссылка на страницу сайта
                       (передается методом from_source)
        """
        raise NotImplementedError(
            '{}._parse_data must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def from_source(self, source):
        data = self._fetch_data(source)
        return self._parse_data(data, source)

    def from_data(self, data):
        return self._parse_data(data)


class SimpleParser(Parser):
    def _parse_data(self, data, source=None):
        data = self._validate_data(data, source)
        if data is None:
            return

        res = {}
        for handler_name, handler_tools in self.handlers.items():
            selector, formatter = handler_tools
            res[handler_name] = formatter(selector(data))
        return self._validate_value(res, source)


class ComplexParser(Parser):
    def __init__(
        self, handlers, loader, parse_data_func=None, *,
        encoding=DEFAULT_ENCODING, coding_errors=DEFAULT_CODING_ERRORS,
        silent=True
    ):
        """

        :param handlers:
        :param parse_data_func: функция, с расширенным методом парсинга данных
                                первый аргумент всегда сам парсер,
                                второй - data, третий - ссылка на страницу
                                (необязательный, по умолчанию None; передается
                                методом from_source);
                                всегда должна возвращать словарь или None
        :param encoding:
        :return:
        """
        super().__init__(
            handlers, loader,
            encoding=encoding, coding_errors=coding_errors, silent=silent,
        )
        self._parse_data_func = parse_data_func

    def _parse_data(self, data, source=None):
        if self._parse_data_func is None:
            raise NotImplementedError(
                '{}._parse_data must be defined in child classes '
                'or passed as init parameter'.format(self.__class__.__name__)
            )

        data = self._validate_data(data, source)
        if data is None:
            return
        res = self._parse_data_func(self, data, source)
        return self._validate_value(res, source)


class FakeParser(Parser):
    def __init__(
        self, handlers=None, loader=None, retval=None, *,
        encoding=DEFAULT_ENCODING, coding_errors=DEFAULT_CODING_ERRORS,
        silent=True
    ):
        """
        Парсер, который возвращает статическое значение.

        Используется, например, когда пагинатор не нужен, а вместо результатов
        нужно возвращать None.

        :param handlers:
        :param loader:
        :param retval: значение, возвращаемое любым методом парсинга
        :param encoding:
        :param silent:
        :return:
        """
        super().__init__(
            handlers, loader,
            encoding=encoding, coding_errors=coding_errors, silent=silent
        )
        self.retval = retval

    def from_data(self, data):
        return self.retval

    def from_source(self, source):
        return self.retval
