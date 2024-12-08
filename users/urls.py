from django.urls import path
from .views import KakaoLoginView

urlpatterns = [
    # path('test/', TestAPIView.as_view(), name='test-api'),
    path('test/', KakaoLoginView.as_view(), name='kakao-login'),
]