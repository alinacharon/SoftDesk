from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all() # Эту строчку удалить
    serializer_class = ProjectSerializer
    #permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]
    # def get_queryset(self):
    #    pk = self.kwargs.get('pk')
    #    if not pk : return Project.objects.all()[:4]
            
    #     return Project.objects.filter(pk=pk)
     
    @action(methods=['get'], detail=True) 
    def contributors(self, request, pk=None):
        try:
            project = Project.objects.get(pk=pk)
            project_contributors = project.contributors.all()
            return Response({'contributors': [c.username for c in project_contributors]})
        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['get'], detail=True)
    def issues(self, request, pk = None):
          issue = Issue.objects.get(pk=pk)
          return Response({'type': issue.type, 'status':issue.status })


# class ProjectAPIList(generics.ListCreateAPIView):
#     #permission_classes = [IsAuthenticated]
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer

# class ProjectAPIDetail(generics.RetrieveUpdateDestroyAPIView):
#     #permission_classes = [IsAuthenticated]
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer


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