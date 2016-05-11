from django.db.models.options import Options as BaseOptions


class Options(BaseOptions):

    def __init__(self, meta, app_label=None):
        super(Options, self).__init__(meta, app_label=app_label)
        self.options = None

    def can_migrate(self, connection):
        return False
