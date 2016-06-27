from django.contrib import admin

from .models import App, Model, Field

class MyAppAdminForm(admin.ModelAdmin): pass

class MyAppAdmin(admin.ModelAdmin): pass

admin.site.register(App, MyAppAdmin)

class MyFieldInline(admin.StackedInline):
    model = Field

class MyModelAdmin(admin.ModelAdmin):
    inlines = [MyFieldInline]

admin.site.register(Model, MyModelAdmin)
