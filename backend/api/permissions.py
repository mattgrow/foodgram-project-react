from rest_framework import permissions


class CurrentUserOrAdminOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.author == user or user.role == user.ADMIN:
            return True
        return request.method in permissions.SAFE_METHODS
