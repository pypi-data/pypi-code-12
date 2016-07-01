from django.db import models


class BaseModel(models.Model):
    """Base model class"""
    created_at = models.DateTimeField(
        verbose_name=_("created_at"), auto_now_add=True)

    updated_at = models.DateTimeField(
        verbose_name=_("updated_at"), auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        if hasattr(self, 'name'):
            return "%s" % self.name
        elif hasattr(self, '__unicode__'):
            return self.__unicode__()


class Vip(BaseModel):
    vip_id = models.PositiveIntegerField()
    pool_id = models.PositiveIntegerField()
    vip_ip = models.CharField(max_length=255, unique=True)

    databaseinfra = models.ForeignKey(
        'physical.DatabaseInfra', related_name="vip_databaseinfra"
    )

    def __unicode__(self):
        return "VIP: id: {}, pool: {}, IP: {}".format(
            self.vip_id, self.pool_id, self.vip_ip
        )
