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

    @action(methods=['get'], detail=True)
    def issues(self, request, pk=None):
        issue = Issue.objects.get(pk=pk)
        return Response({'type': issue.type, 'status': issue.status})


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
