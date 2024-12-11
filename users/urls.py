from rest_framework.routers import DefaultRouter
from django.urls import path

from users.views import TestAPIView, UserDetailAPIView, ProfileImageViewSet


class NoSlashRouter(DefaultRouter):
    """
    URL 끝에 슬래시를 제거하는 라우터
    """
    def __init__(self):
        super().__init__()
        self.trailing_slash = ''  # 슬래시 제거


router = NoSlashRouter()

router.register(r'users/profile-images', ProfileImageViewSet, basename='profile-image')


urlpatterns = [
    path('test/', TestAPIView.as_view(), name='test-api'),
    path('users/<int:id>', UserDetailAPIView.as_view(), name='user-detail'),
] + router.urls