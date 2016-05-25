from django.db import models
from django.utils import timezone
from .utils import ip2int, int2ip


class Registry(models.Model):
    registryDesc = models.CharField(max_length=8)

    def __str__(self):
        return self.registryDesc


class TLD(models.Model):
    domain = models.CharField(db_index=True, max_length=2)
    type = models.CharField(max_length=32, null=True)
    description = models.CharField(max_length=64)
    registry = models.ForeignKey(Registry, blank=True, null=True)
    lastModified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain


class InetNum(models.Model):
    inetNumFrom = models.BigIntegerField(db_index=True)
    inetNumTo = models.BigIntegerField()
    inetNumIPFrom = models.CharField(max_length=15,blank=True)          #Searchable field
    tld = models.ForeignKey(TLD)
    registry = models.ForeignKey(Registry)
    inetNumValid = models.BooleanField(default=False)
    inetNumAllocated = models.BooleanField(default=False)
    lastModified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.inetNumIPFrom = int2ip(self.inetNumFrom)
        return super(InetNum, self).save(*args, **kwargs)

    def IPFrom(self):
        return int2ip(self.inetNumFrom)

    IPFrom.admin_order_field = 'IPFrom'
    IPFrom.short_description = 'IPFrom'

    def IPTo(self):
        return int2ip(self.inetNumTo)

    IPTo.admin_order_field = 'IPTo'
    IPTo.short_description = 'IPTo'

    def __str__(self):
        return self.inetNumIPFrom
