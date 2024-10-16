from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .models import Contributor


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow authors of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    """
    Permission to only allow contributors of a project to access it.
    """

    def has_permission(self, request, view):

        project_id = view.kwargs.get('project_pk')

        if not Contributor.objects.filter(project_id=project_id, user=request.user).exists():
            raise PermissionDenied(
                "Vous n'êtes pas un contributeur de ce projet.")

        return True
