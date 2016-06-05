from rest_framework import permissions


class IsAdminOrOwnOnly(permissions.BasePermission):
    """
    The request is authenticated as an admin user, or is a request done by own user data.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated() and
            (request.user.is_superuser or request.user.is_staff or request.method in permissions.SAFE_METHODS)
        )

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    The request is authenticated as an admin user, or is a request done by own user data.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated() or
            request.method == 'POST'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user