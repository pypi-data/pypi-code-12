from django.contrib import admin

from . import models


admin.site.register(models.AlphaModel)
admin.site.register(models.BetaModel)
admin.site.register(models.TaggedCharPkModel)
admin.site.register(models.AnotherTaggedCharPkModel)
admin.site.register(models.CharPkModel)
admin.site.register(models.AnotherCharPkModel)
