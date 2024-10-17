from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from .permissions import *
from .serializers import *
from .models import *


def check_age(request):
    age = int(request.data.get('age', 0))
    can_data_be_shared = request.data.get('can_data_be_shared', False)

    if can_data_be_shared and age < 15:
        return Response(
            {"error": "Vous devez avoir au moins 15 ans pour pouvoir partager vos données."},
            status=status.HTTP_400_BAD_REQUEST
        )
    return None


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"error": "Vous êtes déjà inscrit."}, status=status.HTTP_400_BAD_REQUEST)

        age_check_response = check_age(request)
        if age_check_response:
            return age_check_response

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Utilisateur enregistré avec succès."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateDestroyAPIView):
    """
    API view for user to manage his profile.
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        age_check_response = check_age(request)
        if age_check_response:
            return age_check_response

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
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        projects = Project.objects.filter(contributor__user=user)

        if not projects.exists():
            raise NotFound("Aucun projet trouvé pour cet utilisateur.")

        return projects

    def get_object(self):
        project_id = self.kwargs.get('pk')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Projet non trouvé.")
        if not Contributor.objects.filter(project=project, user=self.request.user).exists():
            raise PermissionDenied(
                "Vous n'êtes pas contributeur de ce projet.")
        return project

    @action(detail=True, methods=['post'])
    def add_contributor(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Utilisateur non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        if Contributor.objects.filter(user=user, project=project).exists():
            return Response(
                {"error": "L'utilisateur est déjà un contributeur."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Contributor.objects.create(
            user=user,
            project=project,
            role='CONTRIBUTOR'
        )
        return Response({
            "message": f"{user.username} a été ajouté comme contributeur du projet {project.name}."
        })

    @action(detail=True, methods=['delete'])
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
                {"error": "Impossible de supprimer l'auteur du projet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = contributor.user.username
        contributor.delete()

        return Response({
            "message": f"Contributeur {username} supprimé du projet {project.name}."
        })


class IssueViewSet(viewsets.ModelViewSet):
    """
    API view for managing issues within projects.
    """
    serializer_class = IssueSerializer
    permission_classes = [IsOwnerOrReadOnly,
                          IsContributor]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        issue = Issue.objects.filter(project_id=project_id)
        if not issue.exists():
            raise NotFound("Aucun problème trouvé pour ce projet.")
        return issue


class CommentViewSet(viewsets.ModelViewSet):
    """
    API view for managing comments on issues.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly, IsContributor]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        issue_id = self.kwargs.get('issue_pk')
        issue = get_object_or_404(Issue, id=issue_id, project_id=project_id)
        comments = Comment.objects.filter(issue=issue)
        if not comments.exists():
            raise NotFound("Aucun commentaire trouvé pour ce problème.")
        return comments
