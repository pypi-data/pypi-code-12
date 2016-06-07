import tryp.logging
from tryp.logging import tryp_logger
from tryp.lazy import lazy

log = series_root_logger = tryp_logger('series')


def series_logger(name: str):
    return series_root_logger.getChild(name)


class Logging(tryp.logging.Logging):

    @lazy
    def _log(self) -> tryp.logging.Logger:  # type: ignore
        return series_logger(self.__class__.__name__)

__all__ = ('series_logger', 'Logging')
