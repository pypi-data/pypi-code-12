from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnly(BasePermission):
    """
    The request is a read-only request.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
