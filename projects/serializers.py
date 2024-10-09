from rest_framework import serializers

from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer is responsible for creating new user accounts. 
    It includes a password field which is write-only to ensure security.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        """
        Creates a new user instance.

        Args:
            validated_data (dict): The validated data for creating a user.

        Returns:
            User: The newly created user instance.
        """
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.

    This serializer is used to retrieve user information, including
    their associated projects as contributors.
    """
    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'age', 'can_be_contacted',
                  'can_data_be_shared', 'email', 'projects']

    def get_projects(self, obj):
        """
        Retrieves a list of project names associated with the user as a contributor.

        Args:
            obj (User): The user instance for which to retrieve projects.

        Returns:
            list: A list of project names where the user is a contributor.
        """
        projects = Project.objects.filter(contributor__user=obj)
        return [project.name for project in projects]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments on issues.

    This serializer is responsible for validating and serializing
    comment data, including the author who is automatically set to the current user.
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


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for issue details.

    This serializer handles the creation and validation of issues,
    including the assignment of users to the issue.
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
            raise serializers.ValidationError("Project not found.")
        for user in value:
            if not Contributor.objects.filter(project=project, user=user).exists():
                raise serializers.ValidationError(
                    f"User with ID {user.id} is not a contributor of this project.")
        return value

    def create(self, validated_data):
        project_id = self.context['view'].kwargs.get('project_pk')
        validated_data['project_id'] = project_id
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for project details.

    This serializer manages the serialization and validation of project data,
    including its contributors and associated issues.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contributors = serializers.SerializerMethodField()
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['name', 'id', 'description', 'type',
                  'author', 'contributors', 'issues']

    def get_contributors(self, obj):
        """
        Retrieves a list of contributors associated with the project.

        Args:
            obj (Project): The project instance for which to retrieve contributors.

        Returns:
            list: A list of dictionaries containing usernames and their roles.
        """
        contributors = Contributor.objects.filter(project=obj)
        return [{'username': c.user.username, 'role': c.role} for c in contributors]
