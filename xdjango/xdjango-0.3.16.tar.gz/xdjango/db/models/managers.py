from django.db import models


class SafeManager(models.Manager):
    def safe_get(self, **kwargs):
        try:
            return super(SafeManager, self).get(**kwargs)
        except:
            return None

    def get_or_create(self, **kwargs):
        return self.safe_get(**kwargs) or self.create(**kwargs)