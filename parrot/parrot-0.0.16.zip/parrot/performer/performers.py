import logging

from .base import Performer
from .action import register_action


logger = logging.getLogger(__name__)


class ConsolePerformer(Performer):
    # TODO FEATURE: Добавить интернационализацию
    def _print_results(self, total, scs, err):
        # Обработано объектов
        # Собрано успешно
        # Пропущено из-за ошибки
        self._safe_print(
            (
                'Total: {}.\n'
                'Success: {}.\n'
                'Errors: {}.'
            ).format(total, scs, err)
        )

    def _safe_print(self, msg):
        try:
            print(msg)
        except UnicodeError as exc:
            self._raise_if_not_silent(exc, logger)
            logger.warning(exc)

    @register_action(label='clear')
    def clear(self):
        deleted = self.storage.delete_by_label(self.label)
        # Не удалось очистить хранилище
        # Удалено объектов
        self._safe_print(
            'Failed to clean up storage' if deleted is None
            else 'Deleted: {}'.format(deleted)
        )
        return deleted

    @register_action(label='parse')
    def parse_items(self):
        total = scs = err = 0
        if self.clear() is None:
            return
        for item in self.crawler.find_and_parse_items(
            with_section_info=self.with_section_info
        ):
            total += 1
            created_item = self.storage.create(self.serializer(item))
            if created_item is None:
                err += 1
            else:
                scs += 1
                self._safe_print('{}. {}'.format(scs, created_item))
            self._sleep()
        self._print_results(total, scs, err)
        return total, scs, err

    @register_action(label='update')
    def update_items(self):
        total = scs = err = 0
        items = self.storage.select_by_label(self.label)
        if items is None:
            # Ошибка получения объектов для обновления
            self._safe_print('Error retrieving objects to update')
            return
        for item in items:
            total += 1
            # Интерпретировать как булево значение
            updated = self.storage.update(
                self.serializer(self.crawler.parse_item(item.url)), item
            )
            if updated:
                scs += 1
            else:
                err += 1
            # не обновлен
            status = ('' if updated else 'not ') + 'updated'
            self._safe_print('{}. [{}] {}'.format(total, status, item))
            self._sleep()
        self._print_results(total, scs, err)
        return total, scs, err

    @register_action(label='export')
    def export_items(self):
        items = self.storage.select_by_label(self.label)
        if items is None:
            # Ошибка получения объектов для экспорта
            self._safe_print('Error retrieving objects to export')
            return
        total, scs, err = self.exporter(items)
        self._print_results(total, scs, err)
        return total, scs, err


class ConsolePerformerWithExtraClear(ConsolePerformer):
    def __init__(
        self, label, crawler, serializer, storage, exporter,
        extra_clear_func=None, *,
        sleep_sec=0, with_section_info=False, silent=True
    ):
        super().__init__(
            label, crawler, serializer, storage, exporter,
            sleep_sec=sleep_sec,
            with_section_info=with_section_info, silent=silent
        )
        self.extra_clear_func = extra_clear_func

    @register_action(label='clear')
    def clear(self):
        if self.extra_clear_func is not None:
            try:
                self.extra_clear_func()
            except Exception as exc:
                self._raise_if_not_silent(exc)
                logger.error(exc)
        return super().clear()
