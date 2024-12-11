from rest_framework import serializers

from .models import ProfileImage, CustomUser


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id', 'name', 'image']


class UserSerializer(serializers.ModelSerializer):
    image = ProfileImageSerializer()

    class Meta:
        model = CustomUser
        fields = ['name', 'image']
        # fields = ['id', 'name', 'email', 'password', 'kakao_id', 'image', 'is_social', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at']
        # read_only_fields = ['is_social', 'created_at', 'updated_at']


class TestRequestSerializer(serializers.Serializer):
    example_field = serializers.CharField(
        required=True,
        help_text="An example string field",
    )