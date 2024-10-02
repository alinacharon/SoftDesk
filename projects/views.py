from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer
from .models import *
from .serializers import *
from .permissions import *


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"error": "Vous êtes déjà inscrit."}, status=status.HTTP_400_BAD_REQUEST)

        age = int(request.data.get('age'))
        can_data_be_shared = request.data.get('can_data_be_shared')
        if can_data_be_shared and age < 15:
            return Response({"error": "Vous devez avoir au moins 15 ans pour pouvoir partager vos données."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Utilisateur enregistré avec succès."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ProjectViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated, IsOwnerOrReadOnly,ContributorsOnly]
#     queryset = Project.objects.all()  
#     serializer_class = ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly, ContributorsOnly]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if not pk:
           return Project.objects.filter(contributors=self.request.user)
        else:
            return Project.objects.filter(pk=pk)

    @action(methods=['get'], detail=True)
    def issues(self, request, pk=None):
        issue = Issue.objects.get(pk=pk)
        return Response({'type': issue.type, 'status': issue.status})
  
class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsOwnerOrReadOnly, ContributorsOnly]

    def get_queryset(self):
        # Получаем project_pk из URL (вложенные роутеры передают lookup-field)
        project_pk = self.kwargs.get('project_pk')  # Это будет передано из URL
        try:
            project = Project.objects.get(pk=project_pk)
            return Issue.objects.filter(project=project)  # Фильтруем задачи по проекту
        except Project.DoesNotExist:
            return Issue.objects.none()  # Если проект не существует, возвращаем пустой queryset

    def perform_create(self, serializer):
        # Привязываем задачу к проекту и автору
        project_pk = self.kwargs.get('project_pk')  # Получаем идентификатор проекта из URL
        project = Project.objects.get(pk=project_pk)
        serializer.save(project=project, author=self.request.user)  # Сохраняем задачу с проектом и автором

    def create(self, request, *args, **kwargs):
        # Проверяем, является ли пользователь контрибьютором проекта
        project_pk = self.kwargs.get('project_pk')
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        if not Contributor.objects.filter(user=request.user, project=project).exists():
            return Response({"error": "You are not a contributor of this project."}, status=status.HTTP_403_FORBIDDEN)

        # Вызываем родительский метод для создания задачи
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=True)
    def comments(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        return Response({'type': comment.type, 'status': comment.status})


# class ProjectAPIList(generics.ListCreateAPIView):
#     #permission_classes = [IsAuthenticated]
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer

# class ProjectAPIDetail(generics.RetrieveUpdateDestroyAPIView):
#     #permission_classes = [IsAuthenticated]
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
