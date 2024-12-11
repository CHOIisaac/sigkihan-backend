from django.urls import path
from .views import KakaoLoginView, SuperUserLoginView

urlpatterns = [
    path('kakao/login', KakaoLoginView.as_view(), name='kakao-login'),
    path('auth/superuser-login/', SuperUserLoginView.as_view(), name='superuser-login'),
]