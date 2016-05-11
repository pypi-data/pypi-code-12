"""
We just simply add all models in the admin interface.
"""
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .tools import models

# First define custom admin on required models.

# Now register the remaining with the default settings.
for key in models.ALL:
    subject = models.ALL[key]

    try:
        admin.site.register(subject)
    except AlreadyRegistered:
        pass



