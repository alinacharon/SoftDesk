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


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        # Работаем с username вместо user
        slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Contributor
        fields = ['user', 'project', 'issue', 'created_time']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = "__all__"


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assigned_users = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), many=True)

    class Meta:
        model = Issue
        fields = ['name', 'type', 'assigned_users', 'author', 'level']


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    issues = IssueSerializer(many=True, read_only=True)
    contributors = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), many=True)

    class Meta:
        model = Project
        fields = ['name', 'description', 'type',
                  'contributors', 'author', 'issues']
