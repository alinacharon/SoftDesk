from rest_framework import serializers

from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
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
    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'projects']

    def get_projects(self, obj):
        projects = Project.objects.filter(contributors=obj)
        return [project.name for project in projects]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = "__all__"


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assigned_users = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), many=True
    )

    class Meta:
        model = Issue
        fields = ['name', 'type', 'assigned_users',
                  'author', 'level', 'project']

    def validate_assigned_users(self, value):
        project = self.context['view'].get_object().project

        for user in value:
            if not project.contributors.filter(id=user.id).exists():
                raise serializers.ValidationError(
                    f"User {user.username} is not a contributor of this project."
                )
        return value


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    issues = IssueSerializer(many=True, read_only=True)
    contributors = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), many=True
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'type',
                  'contributors', 'author', 'issues']
