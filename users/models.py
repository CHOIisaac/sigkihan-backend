from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=100, blank=True)  # 이름 (선택적)
    email = models.EmailField(unique=True)  # 이메일 (유일 값)
    kakao_id = models.CharField(max_length=50, blank=True, null=True, unique=True)  # 카카오 고유 ID
    image = models.ForeignKey('ProfileImage', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')  # 선택한 이미지
    is_social = models.BooleanField(default=False, help_text="소셜 로그인 여부")  # 소셜 로그인 사용자 구분

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class ProfileImage(models.Model):
    name = models.CharField(max_length=100)  # 이미지 이름
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # 프로필 이미지 경로
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시각

    def __str__(self):
        return f"Profile Image for {self.user.email}"


