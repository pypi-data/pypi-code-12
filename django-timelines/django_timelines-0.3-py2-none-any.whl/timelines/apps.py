from django.apps import AppConfig


class TimelineConfig(AppConfig):
    name = 'timelines'
    verbose_name = "timelines"

    def ready(self):
        from registration import autodiscover
        autodiscover()
