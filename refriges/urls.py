from django.urls import path
from .views import RefrigeratorView

urlpatterns = [
    path('<int:id>', RefrigeratorView.as_view(), name='refrigerator-detail'),
]