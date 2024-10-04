from .models import Project, Issue, Comment
from rest_framework import permissions

from .models import *


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow authors of an object to edit it.

    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class ContributorsOnly(permissions.BasePermission):
    """
    Allows access only to the contributors of the project, its issues, and comments
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if view.action == 'list':
            project_id = request.GET.get('project_id')

            if project_id:
                return Project.objects.filter(id=project_id, contributors=user).exists()

            return Project.objects.filter(contributors=user).exists()

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, Project):
            return user in obj.contributors.all()

        if isinstance(obj, Issue):
            return user in obj.project.contributors.all()

        if isinstance(obj, Comment):
            return user in obj.issue.project.contributors.all()

        return False
