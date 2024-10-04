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
    Позволяет доступ только контрибьюторам проекта или задачи.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Если объект - это проект, проверяем, является ли пользователь контрибьютором
        if isinstance(obj, Project):
            return user in obj.contributors.all()

        # Если объект - это комментарий, проверяем контрибьюторов связанной задачи
        if isinstance(obj, Comment):
            # Получаем связанную задачу
            issue = obj.issue
            return user in issue.project.contributors.all()

        return False
