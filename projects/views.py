from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from .permissions import *
from .serializers import *


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"error": "Vous êtes déjà inscrit."}, status=status.HTTP_400_BAD_REQUEST)

        age = int(request.data.get('age'))
        can_data_be_shared = request.data.get('can_data_be_shared')
        if can_data_be_shared and age < 15:
            return Response({"error": "Vous devez avoir au moins 15 ans pour pouvoir partager vos données."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Utilisateur enregistré avec succès."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [ContributorsOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(contributors=user)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsOwnerOrReadOnly, ContributorsOnly]

    def get_queryset(self):
        user = self.request.user
        return Issue.objects.filter(project__contributors=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['view'] = self
        return context

    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        if not project.contributors.filter(id=request.user.id).exists():
            return Response({"error": f"L'utilisateur {request.user.username} n'est pas un contributeur de ce projet."}, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ContributorsOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(issue__assigned_users=user)


class ContributorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        group = Group.objects.get(name='Contributors')
        return User.objects.filter(groups=group)
