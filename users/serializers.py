from rest_framework import serializers
from django.contrib.auth.models import User

from .models import ProfileImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'kakao_id', 'is_social', 'image']


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id', 'name', 'image']


class TestRequestSerializer(serializers.Serializer):
    example_field = serializers.CharField(
        required=True,
        help_text="An example string field",
    )