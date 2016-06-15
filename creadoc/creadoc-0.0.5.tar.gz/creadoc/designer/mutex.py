# coding: utf-8
import datetime
from m3_mutex import MutexID, capture_mutex, MutexBusy, release_mutex
from m3_mutex.models import MutexModel

__author__ = 'damirazo <me@damirazo.ru>'


class CreadocMutex(object):
    u"""
    Реализация примитивного мьютекса на основе модуля m3-mutex
    """

    def __init__(self, object_id):
        self.object_id = object_id
        self.group = 'creadoc'

    @property
    def mutex_id(self):
        return MutexID(id=self.object_id, group=self.group)

    def row(self):
        return MutexModel.objects.get(
            mutex_group=self.group,
            mutex_id=self.object_id,
        )

    def is_free(self):
        u"""
        Проверка записи на наличие наложенного мьютекса
        :rtype: bool
        """
        try:
            row = self.row()
        except MutexModel.DoesNotExist:
            return True

        captured_since = row.captured_since
        if captured_since.tzinfo:
            captured_since = captured_since.replace(tzinfo=None)

        if captured_since < datetime.datetime.now() - datetime.timedelta(hours=1):  # noqa
            self.release()

            return True

        return False

    def capture(self):
        u"""
        Захват записи мьютексом
        """
        try:
            capture_mutex(self.mutex_id)
        except MutexBusy:
            pass

    def release(self):
        u"""
        Освобождение записи от мьютекса
        """
        try:
            release_mutex(self.mutex_id)
        except MutexBusy:
            pass
