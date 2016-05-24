import time
from parrot.utils import MethodsIfSilentIsDefinedMixin


class Loader(MethodsIfSilentIsDefinedMixin):
    """
    Загрузчик страниц

    Используется парсером для получения содержимого страницы.
    Каждый наследник должен определять метод _load.
    """
    def __init__(self, *, attempts_limit=3, sleep_sec=10, silent=True):
        if sleep_sec < 0:
            raise ValueError(
                'Sleep interval must be greater than 0. Now: {}'.format(
                    sleep_sec
                )
            )
        self.attempts_limit = attempts_limit
        self.sleep_sec = sleep_sec
        self.silent = silent

    def __call__(self, *pargs, **kwargs):
        for _ in range(self.attempts_limit):
            data = self._load(*pargs, **kwargs)
            if data is None:
                # Если возникла ошибка, которая не является допустимой, то спим
                # и переходим к следующей попытке
                self._sleep()
                continue
            if isinstance(data, Exception):
                return None
            return data
        else:
            return None

    def _sleep(self):
        if self.sleep_sec:
            time.sleep(self.sleep_sec)

    def _load(self, source):
        """
        Загрузить данные из источника.

        Если возвращен None, то попытка считается проваленной, а загрузчик
        выполнит следующую попытку.
        Если возвращено исключение (Exception), то попытка считается
        завершенной, но результат не получен, из-за его отсутствия. Загрузчик
        вернет None.
        Иначе загрузчик вернет полученные данные.
        :param source:
        :return:
        """
        raise NotImplementedError(
            '{}._load must be defined in child classes'.format(
                self.__class__.__name__
            )
        )
