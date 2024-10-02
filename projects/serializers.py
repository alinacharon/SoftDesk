from rest_framework import serializers

from .models import *


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Project
        fields = "__all__"


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'age', 'can_be_contacted', 'can_data_be_shared']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password']) 
        user.save()
        return user

class IssueSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contributor = serializers.PrimaryKeyRelatedField(queryset=Contributor.objects.none(), required=False)

    class Meta:
        model = Issue
        fields = ['name', 'description', 'contributor', 'project'] 

    def validate_contributor(self, value):
        # Ensure the contributor of issue is a contributor of the project
        project_id = self.context['view'].kwargs.get('pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            if value not in project.contributors.all():
                raise serializers.ValidationError("Contributor of issue must be a contributor of the project.")
        return value

    def create(self, validated_data):
        # Create the issue with the validated data
        return super().create(validated_data)