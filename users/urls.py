from django.urls import path

from users.views import TestAPIView

urlpatterns = [
    path('test/', TestAPIView.as_view(), name='test-api'),
]