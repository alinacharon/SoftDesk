from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from .models import *


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise AuthenticationFailed('User is not authenticated')
        return True


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
    Allows access only to the contributors of the project, its issues, and comments.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if view.action == 'list':
            project_id = request.GET.get('project_id')
            issue_id = request.GET.get('issue_id')

            if project_id:
                return Contributor.objects.filter(project_id=project_id, user=user).exists()

            if issue_id:
                try:
                    issue = Issue.objects.get(id=issue_id)
                except Issue.DoesNotExist:
                    return False
                return Contributor.objects.filter(project=issue.project, user=user).exists()

            return Contributor.objects.filter(user=user).exists()

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, Project):
            return Contributor.objects.filter(project=obj, user=user).exists()

        if isinstance(obj, Issue):
            return Contributor.objects.filter(project=obj.project, user=user).exists()

        if isinstance(obj, Comment):
            return Contributor.objects.filter(project=obj.issue.project, user=user).exists()

        return False


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser
