from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import site, ModelAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from .models import (DynamicSetting, BooleanDynamicSetting, DecimalDynamicSetting, IntegerDynamicSetting,
                     LongTextDynamicSetting, ShortTextDynamicSetting, JSONDynamicSetting)


class ReadonlyOnEditAdminMixin(ModelAdmin):
    """
    This mixin will disallow the edition of 'name' and 'allow_null' fields
      for any existing object, while allowing them for new objects.
    """

    def get_readonly_fields(self, request, obj=None):
        """
        Determine whether these fields should be editable (new objects) or
          readonly (existing objects).
        """
        readonly_fields = list(super(ReadonlyOnEditAdminMixin, self).get_readonly_fields(request, obj))
        more_fields = ['name', 'allow_null'] if obj else []
        return list(set(readonly_fields + more_fields))


class DerivedDynamicSettingAdmin(PolymorphicChildModelAdmin, ReadonlyOnEditAdminMixin):

    base_model = DynamicSetting
    fields = ['name', 'allow_null', 'value']


class DynamicSettingAdmin(PolymorphicParentModelAdmin, ReadonlyOnEditAdminMixin):

    base_model = DynamicSetting
    polymorphic_list = True
    list_display = ['name', 'display']
    list_display_links = ['name']

    def display(self, obj):
        """
        Read-only callable used to display the actual setting value. Since this is polymorphic, I cannot
          simply add 'value' to list_display, because it is not an actual field on each DynamicSetting.
        """
        return obj.value
    display.short_description = _(u'Value')

    def get_child_models(self):
        """
        One child for each type. They will use the same
        """
        return [
            (BooleanDynamicSetting, DerivedDynamicSettingAdmin),
            (DecimalDynamicSetting, DerivedDynamicSettingAdmin),
            (IntegerDynamicSetting, DerivedDynamicSettingAdmin),
            (LongTextDynamicSetting, DerivedDynamicSettingAdmin),
            (ShortTextDynamicSetting, DerivedDynamicSettingAdmin),
            (JSONDynamicSetting, DerivedDynamicSettingAdmin)
        ]


site.register(DynamicSetting, DynamicSettingAdmin)