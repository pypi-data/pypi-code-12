from django.contrib import admin
from hosted_plugins import models

class DocumentationInlineAdmin(admin.StackedInline):
    model = models.Update.docs.through
    extra = 0

class ChecksumInlineAdmin(admin.TabularInline):
    model = models.Checksum
    extra = 0

class DocumentationAdmin(admin.ModelAdmin):
    list_display = ('title','slug','platforms','num_updates',)
    list_filter = ('slug','updates__platform__platform')
    date_hierarchy = 'created_on'
    inlines = [DocumentationInlineAdmin]
    
    def platforms(self, obj):
        return ','.join([update.platform.platform for update in obj.updates.all()])
    
    def num_updates(self, obj):
        return obj.updates.count()
    num_updates.short_description = 'Updates'

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('platform','version','release_date','downloads',)
    list_filter = ('platform__platform',)
    date_hierarchy = 'release_date'
    inlines = [ChecksumInlineAdmin,DocumentationInlineAdmin]
    exclude = ('docs',)

class PlatformAdmin(admin.ModelAdmin):
    list_display = ('platform','plugin',)
    list_filter = ('platform','plugin',)

admin.site.register(models.Documentation, DocumentationAdmin)
admin.site.register(models.Update, UpdateAdmin)
admin.site.register(models.Platform, PlatformAdmin)
