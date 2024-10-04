from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

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

    @action(methods=['post'], detail=True)
    def add_project_contributors(self, request, pk=None):
        project = self.get_object()  # Получаем проект по первичному ключу из URL
        
        # Проверка, что пользователь является владельцем проекта или контрибьютором
        if not (request.user == project.author or request.user in project.contributors.all()):
            return Response({"error": "You do not have permission to add contributors to this project."}, status=status.HTTP_403_FORBIDDEN)

        # Получаем ID контрибьютора из запроса
        contributor_id = request.data.get('contributor_id')
        if not contributor_id:
            return Response({"error": "Contributor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contributor_to_add = User.objects.get(pk=contributor_id)
        except User.DoesNotExist:
            return Response({"error": "Contributor not found."}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, является ли пользователь уже контрибьютором проекта
        if Contributor.objects.filter(contributor=contributor_to_add, project=project).exists():
            return Response({"error": "This user is already a contributor to this project."}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем нового контрибьютора
        Contributor.objects.create(contributor=contributor_to_add, project=project)

        return Response({"message": f"{contributor_to_add.username} has been added as a contributor."}, status=status.HTTP_201_CREATED)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsOwnerOrReadOnly, ContributorsOnly]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.GET.get('project_id')

        if project_id:
            return Issue.objects.filter(project_id=project_id)
        else:
            return Issue.objects.filter(project__contributors=user)

    @action(methods=['post'], detail=True)
    def add_assigned_user(self, request, pk=None):
        issue = self.get_object()  # Получаем задачу по первичному ключу из URL

        # Проверка, что пользователь является владельцем задачи или контрибьютором проекта
        if not (request.user == issue.author or request.user in issue.project.contributors.all()):
            return Response({"error": "You do not have permission to assign users to this issue."}, status=status.HTTP_403_FORBIDDEN)

        # Получаем ID пользователя из запроса
        assigned_user_id = request.data.get('assigned_user_id')
        if not assigned_user_id:
            return Response({"error": "Assigned user ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assigned_user = User.objects.get(pk=assigned_user_id)
        except User.DoesNotExist:
            return Response({"error": "Assigned user not found."}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, является ли пользователь контрибьютором проекта
        if not Contributor.objects.filter(contributor=assigned_user, project=issue.project).exists():
            return Response({"error": f"User {assigned_user.username} is not a contributor to this project."}, status=status.HTTP_400_BAD_REQUEST)

        # Добавляем пользователя как `assigned_user` к задаче
        issue.assigned_users = Contributor.objects.get(contributor=assigned_user, project=issue.project)
        issue.save()

        return Response({"message": f"{assigned_user.username} has been assigned to this issue."}, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ContributorsOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        issue_id = self.request.GET.get('issue_id')
        queryset = Comment.objects.all()

        if issue_id:
            queryset = queryset.filter(issue_id=issue_id)

        return queryset


class ContributorViewSet(viewsets.ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = Project.objects.get(id=project_id)
        if Contributor.objects.filter(user=self.request.user, project=project).exists():
            serializer.save(user=self.request.user, project=project)
        else:
            raise PermissionDenied(
                "You are not authorized to add contributors to this project.")
