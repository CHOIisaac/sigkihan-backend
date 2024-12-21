from django.urls import path
from .views import RefrigeratorView

urlpatterns = [
    path('<int:id>', RefrigeratorView.as_view(), name='refrigerator-detail'),
    # 초대 생성 API
    path('refrigerators/<int:refrigerator_id>/invite', RefrigeratorView.CreateInvitationView.as_view(), name='create_invitation'),
    # 초대 목록 조회 API
    path('invitations', RefrigeratorView.InvitationListView.as_view(), name='list_invitations'),
    # 초대 상태 업데이트 API (수락/거부)
    path('invitations/<int:invitation_id>/update', RefrigeratorView.UpdateInvitationStatusView.as_view(),
         name='update_invitation_status'),
]
