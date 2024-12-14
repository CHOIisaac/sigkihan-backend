from django.urls import path
from .views import NotificationListView, NotificationMarkAsReadView, CreateNotificationAPIView, \
    CreatePopupNotificationAPIView, PopupNotificationListView, PopupNotificationMarkAsReadView

urlpatterns = [
    path('<int:refrigerator_id>/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('<int:refrigerator_id>/notifications/popup', PopupNotificationListView.as_view(), name='notification-list'),
    path('<int:refrigerator_id>/notifications/mark-as-read', NotificationMarkAsReadView.as_view(), name='notification-mark-as-read'),
    path('<int:refrigerator_id>/notifications/popup/mark-as-read', PopupNotificationMarkAsReadView.as_view(), name='notification-mark-as-read'),
    path('<int:refrigerator_id>/notifications/create', CreateNotificationAPIView.as_view(), name='create-notification'),
    path('<int:refrigerator_id>/notifications/popup/create', CreatePopupNotificationAPIView.as_view(), name='create-notification'),
]