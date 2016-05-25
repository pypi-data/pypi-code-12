from django.contrib import admin
from iprir.models import TLD, Registry, InetNum

class tldAdmin(admin.ModelAdmin):
    fields = ['domain', 'type', 'description', 'registry']
    list_display = ('domain', 'type', 'description')
    ordering = ['domain']
    search_fields = ['description']

class registryAdmin(admin.ModelAdmin):
    ordering = ['registryDesc']

class inetnumAdmin(admin.ModelAdmin):
    fields = ['inetNumFrom', 'inetNumTo', 'tld', 'registry', 'inetNumValid', 'inetNumAllocated']
    list_display = ('inetNumFrom', 'inetNumTo', 'IPFrom', 'IPTo', 'tld', 'registry', 'inetNumValid', 'inetNumAllocated', 'lastModified')
    ordering = ['inetNumFrom']
    search_fields = ['inetNumIPFrom']


admin.site.register(TLD, tldAdmin)
admin.site.register(InetNum, inetnumAdmin)
admin.site.register(Registry, registryAdmin)
