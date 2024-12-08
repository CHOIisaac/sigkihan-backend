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


class KakaoLoginRequestSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True,
        help_text="카카오 로그인 후 받은 Authorization Code"
    )


class KakaoLoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="JWT Refresh Token (장기 유효 토큰)")
    access = serializers.CharField(help_text="JWT Access Token (단기 유효 토큰)")
    user = serializers.DictField(
        child=serializers.CharField(),
        help_text="사용자 정보 (ID, 이메일, 닉네임, 프로필 이미지)"
    )

# class TestRequestSerializer(serializers.Serializer):
#     example_field = serializers.CharField(
#         required=True,
#         help_text="An example string field",
#     )