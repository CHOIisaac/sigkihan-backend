from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RefrigeratorViewSet, InvitationListView, RefrigeratorInvitationView, \
    InvitationStatusUpdateView, RefrigeratorMemoView, RefrigeratorMemoDetailView, RemoveMemberView, LeaveRefrigeratorView


class NoSlashRouter(DefaultRouter):
    """
    URL 끝에 슬래시를 제거하는 라우터
    """
    def __init__(self):
        super().__init__()
        self.trailing_slash = ''  # 슬래시 제거


router = NoSlashRouter()
router.register('refrigerators', RefrigeratorViewSet, basename='refrigerators')

urlpatterns = [
    # 초대 생성 API
    path('refrigerators/<int:refrigerator_id>/invitations', RefrigeratorInvitationView.as_view(), name='refrigerator-invite'),
    path('refrigerators/invitations/<str:invitation_code>', InvitationStatusUpdateView.as_view(), name='invitation-status-update'),
    path('refrigerators/invitations', InvitationListView.as_view(), name='invitation-list'),
    # 초대된 멤버 내보내기
    path('refrigerators/<int:refrigerator_id>/members/<int:member_id>', RemoveMemberView.as_view(), name='remove-member'),
    path('refrigerators/<int:refrigerator_id>/members/self', LeaveRefrigeratorView.as_view(), name='leave-refrigerator'),
    # 냉장고 메모 관련 API
    path('refrigerators/<int:refrigerator_id>/memos', RefrigeratorMemoView.as_view(), name='refrigerator-memo'), # 메모 목록 및 생성
    path('refrigerators/<int:refrigerator_id>/memos/<int:memo_id>', RefrigeratorMemoDetailView.as_view(),
         name='refrigerator-memo-detail'),  # 메모 수정, 삭제
] + router.urls

