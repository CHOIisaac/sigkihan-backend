from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from refriges.models import RefrigeratorAccess, Refrigerator, RefrigeratorInvitation
from refriges.serializers import RefrigeratorSerializer
from users.models import CustomUser


@extend_schema(
        tags=["Refrigerators"],
        summary="사용자의 냉장고 조회",
)
class RefrigeratorView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RefrigeratorSerializer

    def get(self, request, id=None):

        # 현재 사용자가 접근할 수 있는 냉장고 조회
        try:
            refrigerator = Refrigerator.objects.get(id=id)
        except Refrigerator.DoesNotExist:
            return Response({"detail": "Refrigerator not found."}, status=404)

        # 직렬화
        serializer = RefrigeratorSerializer(refrigerator)
        return Response(serializer.data, status=200)


class RefrigeratorInviteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="냉장고 초대 생성",
        description="특정 냉장고에 사용자를 초대합니다. 초대는 냉장고의 소유자만 생성할 수 있습니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "invited_user_id": {"type": "integer", "example": 2, "description": "초대받을 사용자의 ID"}
                },
                "required": ["invited_user_id"]
            }
        },
        responses={
            201: {"description": "초대가 성공적으로 생성되었습니다."},
            403: {"description": "권한이 없습니다. (냉장고 소유자가 아닌 경우)"},
            404: {"description": "냉장고 또는 초대받는 사용자를 찾을 수 없습니다."},
        },
    )
    def post(self, request, refrigerator_id):
        inviter = request.user
        invited_user_id = request.data.get('invited_user_id')
        invited_user = get_object_or_404(CustomUser, pk=invited_user_id)

        refrigerator = get_object_or_404(Refrigerator, pk=refrigerator_id)
        if not RefrigeratorAccess.objects.filter(user=inviter, refrigerator=refrigerator, role='owner').exists():
            return Response({"error": "You are not the owner of this refrigerator."}, status=403)

        RefrigeratorInvitation.objects.create(
            refrigerator=refrigerator,
            invited_user=invited_user,
            inviter=inviter
        )
        return Response({"message": "Invitation sent successfully."}, status=201)


class RefrigeratorInviteStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="초대 상태 변경",
        description="초대를 수락하거나 거절합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["accepted", "declined"], "example": "accepted", "description": "수락 또는 거절 상태"}
                },
                "required": ["status"]
            }
        },
        responses={
            200: {"description": "초대 상태가 성공적으로 업데이트되었습니다."},
            400: {"description": "잘못된 상태 값이 요청되었습니다."},
            404: {"description": "해당 초대를 찾을 수 없습니다."},
        },
    )
    def patch(self, request, invite_id):
        invite = get_object_or_404(RefrigeratorInvitation, pk=invite_id, invited_user=request.user)
        status = request.data.get('status')

        if status not in ['accepted', 'declined']:
            return Response({"error": "Invalid status."}, status=400)

        invite.status = status
        invite.save()

        if status == 'accepted':
            RefrigeratorAccess.objects.create(
                user=request.user,
                refrigerator=invite.refrigerator,
                role='shared'
            )
            return Response({"message": "Invitation accepted. Access granted to refrigerator."}, status=200)

        return Response({"message": "Invitation declined."}, status=200)


class InvitationListView(APIView):
    @extend_schema(
        summary="초대 목록 조회",
        description="사용자가 보낸 초대 및 받은 초대 목록을 조회합니다.",
        responses={
            200: {
                "description": "초대 목록이 성공적으로 조회되었습니다.",
                "examples": {
                    "application/json": {
                        "received_invitations": [
                            {"id": 1, "refrigerator": "가족 냉장고", "status": "pending"},
                            {"id": 2, "refrigerator": "친구 냉장고", "status": "accepted"}
                        ],
                        "sent_invitations": [
                            {"id": 3, "refrigerator": "내 냉장고", "status": "pending"}
                        ]
                    }
                }
            }
        }
    )
    def get(self, request):
        received_invitations = RefrigeratorInvitation.objects.filter(invited_user=request.user)
        sent_invitations = RefrigeratorInvitation.objects.filter(inviter=request.user)

        data = {
            "received_invitations": [
                {"id": invitation.id, "refrigerator": invitation.refrigerator.name, "status": invitation.status}
                for invitation in received_invitations
            ],
            "sent_invitations": [
                {"id": invitation.id, "refrigerator": invitation.refrigerator.name, "status": invitation.status}
                for invitation in sent_invitations
            ],
        }
        return Response(data, status=status.HTTP_200_OK)