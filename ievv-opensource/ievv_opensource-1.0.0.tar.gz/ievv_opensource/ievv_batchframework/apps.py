from django.apps import AppConfig
from django_cradmin.superuserui import superuserui_registry


class BatchOperationAppConfig(AppConfig):
    name = 'ievv_opensource.ievv_batchframework'
    verbose_name = "IEVV batch operation"

    def ready(self):
        appconfig = superuserui_registry.default.add_djangoapp(
            superuserui_registry.DjangoAppConfig(app_label='ievv_batchframework'))
        appconfig.add_all_models()
