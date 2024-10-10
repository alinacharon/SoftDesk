from django.contrib.auth.models import User
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import *
from .serializers import *


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    """
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


class UserProfileView(RetrieveUpdateDestroyAPIView):
    """
    API view for user to managing his profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API view for managing projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [ContributorsOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(contributor__user=user)

    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def add_contributor(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        if Contributor.objects.filter(user=user, project=project).exists():
            return Response(
                {"error": "L'utilisateur est déjà un contributeur"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Contributor.objects.create(
            user=user,
            project=project,
            role='CONTRIBUTOR'
        )
        return Response({
            "message": f"{user.username} a été ajouté comme contributeur du projet {project.name}"
        })

    @action(detail=True, methods=['delete'], permission_classes=[IsOwnerOrReadOnly])
    def remove_contributor(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')

        try:
            contributor = Contributor.objects.get(
                user_id=user_id,
                project=project
            )
        except Contributor.DoesNotExist:
            return Response(
                {"error": "Contributeur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        if contributor.role == 'AUTHOR':
            return Response(
                {"error": "Impossible de supprimer l'auteur du projet"},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = contributor.user.username
        contributor.delete()

        return Response({
            "message": f"Contributeur {username} supprimé du projet {project.name}"
        })


class IssueViewSet(viewsets.ModelViewSet):
    """
    API view for managing issues within projects.
    """
    serializer_class = IssueSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return Issue.objects.filter(project_id=project_id)

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_pk')

        if not project_id:
            return Response({"error": "ID du projet requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Projet non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        if not Contributor.objects.filter(project=project, user=request.user).exists():
            return Response({"error": f"L'utilisateur {request.user.username} n'est pas un contributeur de ce projet."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API view for managing comments on issues.
    """
    serializer_class = CommentSerializer
    permission_classes = [ContributorsOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        issue_id = self.kwargs.get('issue_pk')
        return Comment.objects.filter(issue_id=issue_id)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    API view for managing contributors associated with projects.
    """
    serializer_class = UserSerializer
    permission_classes = [ContributorsOnly]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        return User.objects.filter(contributor__project_id=project_id).distinct()
