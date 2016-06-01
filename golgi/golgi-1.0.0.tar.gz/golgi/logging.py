import tryp.logging
from tryp.logging import tryp_logger
from tryp.lazy import lazy

log = golgi_root_logger = tryp_logger('golgi')


def golgi_logger(name: str):
    return golgi_root_logger.getChild(name)


class Logging(tryp.logging.Logging):

    @lazy
    def _log(self) -> tryp.logging.Logger:  # type: ignore
        return golgi_logger(self.__class__.__name__)

__all__ = ('golgi_logger', 'Logging')
