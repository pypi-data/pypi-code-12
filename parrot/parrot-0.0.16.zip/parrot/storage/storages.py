import logging
from parrot.utils import traceback_in_one_line
from parrot.exceptions import (
    PeeweeStorageSavedObjectIsNotDict, PeeweeStorageCreatingException,
    PeeweeStorageUpdatingException, PeeweeStorageSelectByLabelException,
    PeeweeStorageDeleteByLabelException
)
try:
    import peewee
except ImportError:
    peewee = None

from .base import Storage


logger = logging.getLogger(__name__)


if peewee is not None:
    class PeeweeStorage(Storage):
        def __init__(self, model, *, silent=True):
            super().__init__(silent=silent)
            self.model = model

        def _is_valid_obj(self, obj):
            if not isinstance(obj, dict):
                exc = PeeweeStorageSavedObjectIsNotDict(self.model, obj)
                self._raise_if_not_silent(exc, logger)
                logger.warning(exc)
                return False
            return True

        def get_fields(self):
            return [field[0] for field in self.model._meta.get_sorted_fields()]

        def create(self, obj):
            if not self._is_valid_obj(obj):
                return
            try:
                return self.model.create(**obj)
            except Exception as exc:
                custom_exc = PeeweeStorageCreatingException(
                    self.model, obj, exc, traceback_in_one_line()
                )
                self._raise_if_not_silent(custom_exc, logger)
                logger.warning(custom_exc)
                return

        def update(self, obj, peewee_obj):
            if not self._is_valid_obj(obj):
                return
            try:
                for k, v in obj.items():
                    setattr(peewee_obj, k, v)
                return peewee_obj.save()
            except Exception as exc:
                custom_exc = PeeweeStorageUpdatingException(
                    self.model, obj, peewee_obj, exc, traceback_in_one_line()
                )
                self._raise_if_not_silent(custom_exc, logger)
                logger.warning(custom_exc)
                return

        def select_by_label(self, label):
            try:
                return self.model.select_by_label(label)
            except Exception as exc:
                custom_exc = PeeweeStorageSelectByLabelException(
                    self.model, label, exc, traceback_in_one_line()
                )
                self._raise_if_not_silent(custom_exc, logger)
                logger.warning(custom_exc)
                return

        def delete_by_label(self, label):
            try:
                return self.model.delete_by_label(label)
            except Exception as exc:
                custom_exc = PeeweeStorageDeleteByLabelException(
                    self.model, label, exc, traceback_in_one_line()
                )
                self._raise_if_not_silent(custom_exc, logger)
                logger.warning(custom_exc)
                return
