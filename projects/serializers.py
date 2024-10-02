from rest_framework import serializers

from .models import *


class ProjectSerializer(serializers.ModelSerializer):
    #author = serializers.HiddenField(default=serializers.CurrentUserDefault())
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

