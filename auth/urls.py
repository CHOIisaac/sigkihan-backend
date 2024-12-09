from django.urls import path
from .views import KakaoLoginView

urlpatterns = [
    path('kakao/login', KakaoLoginView.as_view(), name='kakao-login'),
]