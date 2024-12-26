from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RefrigeratorViewSet, InvitationListView, RefrigeratorInvitationView, \
    InvitationStatusUpdateView, RefrigeratorMemoView, RefrigeratorMemoDetailView


router = DefaultRouter()
router.register(r'refrigerators', RefrigeratorViewSet, basename='refrigerators')

urlpatterns = [
    # path('', RefrigeratorViewSet.as_view(), name='refrigerator-list'),
    # path('<int:refrigerator_id>', RefrigeratorViewSet.as_view(), name='refrigerator-detail'),
    # 초대 생성 API
    path('<int:refrigerator_id>/invitations', RefrigeratorInvitationView.as_view(), name='refrigerator-invite'),
    path('invitations/<int:invite_id>', InvitationStatusUpdateView.as_view(), name='invitation-status-update'),
    path('invitations', InvitationListView.as_view(), name='invitation-list'),
    # 냉장고 메모 관련 API
    path('refrigerators/<int:refrigerator_id>/memos/', RefrigeratorMemoView.as_view(), name='refrigerator-memo'), # 메모 목록 및 생성
    path('refrigerators/<int:refrigerator_id>/memos/<int:memo_id>/', RefrigeratorMemoDetailView.as_view(),
         name='refrigerator-memo-detail'),  # 메모 수정, 삭제
] + router.urls

