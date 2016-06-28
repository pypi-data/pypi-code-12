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


class VIP(BaseModel):
    vip_id = models.PositiveIntegerField()
    environment_id = models.PositiveIntegerField()
    ip_id = models.PositiveIntegerField()

    ipv4_id = models.PositiveIntegerField()
    ipv4_ip = models.IPAddressField()

    dscp = models.PositiveIntegerField(null=True)


class Equipment(BaseModel):
    equipment_id = models.PositiveIntegerField()
    vip = models.ForeignKey(
        VIP, related_name="networkapi_equipment", null=False, blank=False
    )
    host = models.ForeignKey(
        Host, related_name="networkapi_host", null=False, blank=False
    )
