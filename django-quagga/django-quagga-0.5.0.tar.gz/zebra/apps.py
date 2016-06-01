"""
Default application configuration
"""

from django.apps.config import AppConfig


class ZebraConfig(AppConfig):
    name = "zebra"
    verbose_name = "Zebra"

    def ready(self):
        pass
