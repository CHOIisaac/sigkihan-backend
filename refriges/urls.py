from django.urls import path
from .views import RefrigeratorListView

urlpatterns = [
    path('refrigerators/<int:id>', RefrigeratorListView.as_view(), name='refrigerator-detail'),
]