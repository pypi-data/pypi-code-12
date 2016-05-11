from django.db import models
from randomfields.models.fields.string import RandomCharField
from randomfields.models.fields.integer import NarrowPositiveIntegerField, RandomIntegerIdentifierField
from uuid import uuid4

def unique_related_name():
    return "r{}".format(uuid4().hex)

class TestPrimaryKey(models.Model):
    id = RandomCharField(primary_key=True, max_length=10)

class TestUnique(models.Model):
    unique_field = RandomCharField(unique=True, max_length=10)

class TestNonUniqueIntegrityError(models.Model):
    unique_int_field = models.IntegerField(unique=True)
    non_unique_field = RandomCharField(max_length=10)

class TestUniqueNotExistIntegrityError(models.Model):
    unique_int_field = models.IntegerField(unique=True)
    unique_rand_field = RandomCharField(unique=True, max_length=10)

class TestMinLengthPossibilities(models.Model):
    data = RandomCharField(unique=True, max_length=2, min_length=1, valid_chars="ab")

class TestFixLengthPossibilities(models.Model):
    data = RandomCharField(unique=True, max_length=2, valid_chars="ab")

class TestIdentifierValue(models.Model):
    id = RandomIntegerIdentifierField(primary_key=True, editable=True)

class TestIdentifierData(models.Model):
    data = RandomIntegerIdentifierField()

class TestIdentifierO2OValue(models.Model):
    id = models.OneToOneField(TestIdentifierValue, primary_key=True, editable=True)

class TestIdentifierFKValue(models.Model):
    data = models.ForeignKey(TestIdentifierValue)

class TestIdentifierM2MValue(models.Model):
    data = models.ManyToManyField(TestIdentifierValue, blank=True)

class TestIdentifierAllValue(models.Model):
    o2o = models.OneToOneField(TestIdentifierValue, related_name='+')
    fk = models.ForeignKey(TestIdentifierValue, related_name='+')
    m2m = models.ManyToManyField(TestIdentifierValue, blank=True, related_name=unique_related_name())

class TestIdentifierM2MO2OPKValue(models.Model):
    id = models.OneToOneField(TestIdentifierValue, primary_key=True, editable=True, related_name=unique_related_name())
    m2m = models.ManyToManyField(TestIdentifierValue, blank=True, related_name=unique_related_name())

class TestIdentifierM2MO2OValue(models.Model):
    o2o = models.OneToOneField(TestIdentifierValue, related_name='+')
    m2m = models.ManyToManyField(TestIdentifierValue, blank=True, related_name=unique_related_name())

class TestIdentifierM2MFKValue(models.Model):
    fk = models.ForeignKey(TestIdentifierValue, related_name='+')
    m2m = models.ManyToManyField(TestIdentifierValue, blank=True, related_name='+')

class TestMaskedAttrDetection(models.Model):
    _randomfields_available_values_for_data = "masked"
    data = RandomIntegerIdentifierField()

class TestNPIFieldChecks(models.Model):
    data = NarrowPositiveIntegerField()