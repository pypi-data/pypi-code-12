
"""
Test models.
"""
from django.db.models import Model, CharField, BooleanField, DateTimeField

#raise IOError("A")

class Thing(Model):
    name = CharField(max_length=32)
    #value = BooleanField(default=False)

