import logging
from parrot.utils import MethodsIfSilentIsDefinedMixin, traceback_in_one_line
from parrot.exceptions import FormatterFormatException


logger = logging.getLogger(__name__)


class Formatter(MethodsIfSilentIsDefinedMixin):
    """
    Принимает всегда один аргумент - значение, найденное селектором

    Обрабатывает значение и представляет в заданном формате для сохранения.
    """
    def __init__(self, format_func=None, *, allow_none=False, silent=True):
        self._format_func = format_func
        self.allow_none = allow_none
        self.silent = silent

    def _format(self, val):
        if self._format_func is None:
            raise NotImplementedError(
                '{}._format must be defined in child classes '
                'or passed as init parameter'.format(self.__class__.__name__)
            )
        return self._format_func(val)

    def __call__(self, val):
        raise NotImplementedError(
            '{}.__call__ must be defined in child classes'.format(
                self.__class__.__name__
            )
        )


class SingleFormatter(Formatter):
    def __call__(self, val):
        if val is None and not self.allow_none:
            return
        try:
            return self._format(val)
        except Exception as exc:
            custom_exc = FormatterFormatException(
                val, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc, logger)
            logger.error(custom_exc)
            return None


_single_formatter_call = SingleFormatter.__call__


class MultiFormatter(Formatter):
    def __call__(self, vals):
        return [_single_formatter_call(self, val) for val in vals]


class FakeFormatter(Formatter):
    def __init__(
        self, format_func=None, retval=None, *, allow_none=False, silent=True
    ):
        super().__init__(format_func, allow_none=allow_none, silent=silent)
        self.retval = retval

    def _format(self, val):
        return self.retval


class SingleFakeFormatter(FakeFormatter, SingleFormatter):
    pass


class MultiFakeFormatter(FakeFormatter, MultiFormatter):
    pass
