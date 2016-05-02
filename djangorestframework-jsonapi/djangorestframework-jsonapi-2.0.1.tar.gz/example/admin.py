from django.contrib import admin
from example import models

admin.site.register(models.Blog)
admin.site.register(models.Entry)
admin.site.register(models.Author)
admin.site.register(models.AuthorBio)
admin.site.register(models.Comment)
