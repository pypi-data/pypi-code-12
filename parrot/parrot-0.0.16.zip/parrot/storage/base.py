from parrot.utils import MethodsIfSilentIsDefinedMixin


class Storage(MethodsIfSilentIsDefinedMixin):
    """ Хранилище результатов парсинга """
    def __init__(self, *, silent=True):
        self.silent = silent

    def _is_valid_obj(self, obj):
        raise NotImplementedError(
            '{}._is_valid_obj must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def get_fields(self):
        raise NotImplementedError(
            '{}.get_fields must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def create(self, obj):
        raise NotImplementedError(
            '{}.create must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def update(self, obj, peewee_obj):
        raise NotImplementedError(
            '{}.update must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def select_by_label(self, label):
        raise NotImplementedError(
            '{}.select_by_label must be defined in child classes'.format(
                self.__class__.__name__
            )
        )

    def delete_by_label(self, label):
        raise NotImplementedError(
            '{}.delete_by_label must be defined in child classes'.format(
                self.__class__.__name__
            )
        )
