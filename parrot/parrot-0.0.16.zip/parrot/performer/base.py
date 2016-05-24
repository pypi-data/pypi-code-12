import time
from parrot.utils import MethodsIfSilentIsDefinedMixin

from .action import get_actions


class Performer(MethodsIfSilentIsDefinedMixin):
    """
    Объединяет работу паука, сериализатора, хранилища и экспортера
    """
    def __init__(
        self, label, crawler, serializer, storage, exporter, *,
        sleep_sec=0, with_section_info=False, silent=True
    ):
        if sleep_sec < 0:
            raise ValueError(
                'Sleep interval must be greater than 0. Now: {}'.format(
                    sleep_sec
                )
            )
        self.label = label
        self.crawler = crawler
        self.serializer = serializer
        self.storage = storage
        self.exporter = exporter
        self.sleep_sec = sleep_sec
        self.with_section_info = with_section_info
        self.silent = silent

    def __str__(self):
        return '{}'.format(self.label)

    def _sleep(self):
        if self.sleep_sec:
            time.sleep(self.sleep_sec)

    @property
    def actions(self):
        """
        :return: список действий (список bounded методов)
        """
        return [
            getattr(self, action.__name__)
            for action in get_actions(self.__class__)
        ]

    def clear(self):
        """
        Очистить хранилище

        Обычно применяется перед парсингом, чтобы удалить старые записи по
        всему проекту
        :return:
        """
        raise NotImplementedError(
            '{}.clear must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def parse_items(self):
        """
        Найти и спарсить все имеющиеся объекты

        :return:
        """
        raise NotImplementedError(
            '{}.parse_items must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def update_items(self):
        """
        Обновить сохраненные в хранилище объекты

        :return:
        """
        raise NotImplementedError(
            '{}.update_items must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def export_items(self):
        """
        Выгрузить сохраненные в хранилище объекты

        :return:
        """
        raise NotImplementedError(
            '{}.export_items must be defined in child classes'.format(
                self.__class__.__name__
            )
        )
