

class NotDeletableAdminMixin(object):

    def get_actions(self, request):
        actions = super(NotDeletableAdminMixin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


class NotAddableAdminMixin(object):

    def has_add_permission(self, request):
        return False
