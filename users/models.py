from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models

from refriges.models import Refrigerator, RefrigeratorAccess


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """일반 사용자 생성"""
        if not email:
            raise ValueError("이메일은 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """슈퍼유저 생성"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("슈퍼유저는 is_staff=True여야 합니다.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("슈퍼유저는 is_superuser=True여야 합니다.")

        user = self.create_user(email, password, **extra_fields)

        # 기본 냉장고 생성
        refrigerator = Refrigerator.objects.create(
            name=f"{user.name or '관리자'}의 냉장고",
            description="슈퍼유저 기본 냉장고"
        )
        RefrigeratorAccess.objects.create(
            user=user,
            refrigerator=refrigerator,
            role='owner'
        )

        return user


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=100, blank=True, verbose_name='닉네임')  # 이름 (선택적)
    email = models.EmailField(unique=True, verbose_name='이메일')  # 이메일 (유일 값)
    password = models.CharField(max_length=128, verbose_name="비밀번호")
    kakao_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name='카카오 고유 ID')  # 카카오 고유 ID
    image = models.ForeignKey('ProfileImage', default=1, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='프로필 이미지')  # 선택한 이미지
    is_social = models.BooleanField(default=False, verbose_name="소셜 로그인 여부", )  # 소셜 로그인 사용자 구분
    is_active = models.BooleanField(default=True, verbose_name="활성 사용자 여부")
    is_staff = models.BooleanField(default=False, verbose_name="스태프 권한")  # 관리자 여부
    is_superuser = models.BooleanField(default=False, verbose_name="슈퍼유저 권한")  # 슈퍼유저 여부
    updated_at = models.DateTimeField(auto_now=True, verbose_name="정보 수정 날짜")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="가입 날짜")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # 슈퍼유저 생성 시 추가로 요구하는 필드

    objects = CustomUserManager()  # 사용자 매니저 연결

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'user'
        verbose_name = '사용자'


class ProfileImage(models.Model):
    name = models.CharField(max_length=100, verbose_name='이미지 이름')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name='프로필 이미지')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='이미지 생성 시간')  # 생성 시각

    def __str__(self):
        return f"Profile Image for {self.name}"

    class Meta:
        db_table = 'profile_image'
        verbose_name = '프로필 이미지'

