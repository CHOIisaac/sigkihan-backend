from django.urls import path
from .views import NotificationListView, NotificationMarkAsReadView, CreateNotificationAPIView

urlpatterns = [
    path('<int:refrigerator_id>/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('<int:refrigerator_id>/notifications/<int:notification_id>/mark-as-read', NotificationMarkAsReadView.as_view(), name='notification-mark-as-read'),
    path('refrigerators/<int:refrigerator_id>/notifications/create/', CreateNotificationAPIView.as_view(), name='create-notification'),
]