from django.urls import path
from .views import KakaoLoginView, KakaoLoginRedirectView

urlpatterns = [
    # path('test/', TestAPIView.as_view(), name='test-api'),
    path('callback/kakao/', KakaoLoginView.as_view(), name='kakao-login'),
]