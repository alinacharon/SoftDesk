from rest_framework import serializers

from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    """
    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'age', 'can_be_contacted',
                  'can_data_be_shared', 'projects']

    def get_projects(self, obj):
        projects = Project.objects.filter(contributor__user=obj).distinct()
        project_names = set([project.name for project in projects])
        return list(project_names)


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments on issues.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ['id', 'description', 'author',
                  'created_time', 'updated_time']

    def create(self, validated_data):
        issue_id = self.context['view'].kwargs.get('issue_pk')
        validated_data['issue_id'] = issue_id
        return super().create(validated_data)


class IssueListSerializer(serializers.ModelSerializer):
    """
    Serializer for issue list.
    """

    class Meta:
        model = Issue
        fields = ['id', 'name', 'status']


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for issue details.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assigned_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )
    comments = CommentSerializer(
        many=True, read_only=True, source='comment_set')

    class Meta:
        model = Issue
        fields = ['name', 'id', 'type', 'assigned_users',
                  'author', 'level', 'comments', 'created_time', 'updated_time', 'status']

    def validate_assigned_users(self, value):
        project_id = self.initial_data.get(
            'project') or self.context['view'].kwargs.get('project_pk')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Projet non trouvé.")
        for user in value:
            if not Contributor.objects.filter(project=project, user=user).exists():
                raise serializers.ValidationError(
                    f"L'utilisateur avec l'ID {user.id} n'est pas un contributeur de ce projet.")
        return value

    def create(self, validated_data):
        project_id = self.context['view'].kwargs.get('project_pk')
        validated_data['project_id'] = project_id
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for project details.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contributors = serializers.SerializerMethodField()
    issues = IssueListSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['name', 'id', 'description', 'type',
                  'author', 'contributors', 'issues']

    def get_contributors(self, obj):
        contributors = Contributor.objects.filter(project=obj)
        return [{'username': c.user.username, 'role': c.role} for c in contributors]
