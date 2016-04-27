""" Customisation for the admin interface. """

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from .models import GroupProfile


# Register your models here.
class GroupProfileInline(admin.StackedInline):
    """
    The in-line display of the Group Profile.

    """
    model = GroupProfile
    can_delete = False
    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'
    list_display = ('doi_suffix')


# pylint: disable=too-many-public-methods
class MyGroupAdmin(GroupAdmin):
    """
    Customise GroupAdmin.

    """
    inlines = [GroupProfileInline]
    list_display = ('name', 'get_doi')

    # pylint: disable=no-self-use
    def get_doi(self, obj):
        """
        Get the DOI suffix.

        """
        doi_suffix = ''
        try:
            doi_suffix = obj.groupprofile.doi_suffix
        except AttributeError:
            pass
        return doi_suffix

    get_doi.short_description = 'doi suffix'


# Re-register GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)
