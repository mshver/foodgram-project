from rest_framework.permissions import SAFE_METHODS, BasePermission

class CreatorOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.creator == request.user

class AdminOrRead(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or 
                request.user and request.user.is_staff)