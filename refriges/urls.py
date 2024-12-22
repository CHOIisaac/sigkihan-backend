from django.urls import path
from .views import RefrigeratorView, InvitationListView, RefrigeratorInvitationView, \
    InvitationStatusUpdateView

urlpatterns = [
    path('<int:id>', RefrigeratorView.as_view(), name='refrigerator-detail'),
    # 초대 생성 API
    path('<int:refrigerator_id>/invitations', RefrigeratorInvitationView.as_view(), name='refrigerator-invite'),
    path('invitations/<int:invite_id>', InvitationStatusUpdateView.as_view(), name='invitation-status-update'),
    path('invitations', InvitationListView.as_view(), name='invitation-list'),
]

