from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
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


class RefrigeratorInvitationView(APIView):
    """
    냉장고 초대 생성
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="냉장고 초대 생성",
        description="특정 냉장고에 사용자를 초대합니다. 초대하려면 요청자가 냉장고 소유자여야 합니다.",
        # parameters=[
        #     OpenApiParameter(name="refrigerator_id", description="냉장고 ID", required=True, type=int)
        # ],
        tags=["Refrigerators"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "invited_user_id": {"type": "integer", "example": 5, "description": "초대할 사용자 ID"}
                },
                "required": ["invited_user_id"]
            }
        },
        responses={
            201: {"description": "Invitation sent successfully."},
            403: {"description": "You are not the owner of this refrigerator."},
            404: {"description": "Refrigerator or invited user not found."},
        }
    )
    def post(self, request, refrigerator_id):
        inviter = request.user
        invited_user_id = request.data.get('invited_user_id')
        invited_user = get_object_or_404(CustomUser, pk=invited_user_id)

        # 냉장고 접근 확인
        refrigerator = get_object_or_404(Refrigerator, pk=refrigerator_id)
        if not RefrigeratorAccess.objects.filter(user=inviter, refrigerator=refrigerator, role='owner').exists():
            return Response({"error": "You are not the owner of this refrigerator."}, status=403)

        # 초대 생성
        RefrigeratorInvitation.objects.create(
            refrigerator=refrigerator,
            invited_user=invited_user,
            inviter=inviter
        )
        return Response({"message": "Invitation sent successfully."}, status=201)


class InvitationStatusUpdateView(APIView):
    """
    초대 상태 업데이트
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="초대 상태 업데이트",
        description="사용자가 받은 초대의 상태를 수락(accepted) 또는 거절(declined)로 변경합니다.",
        parameters=[
            OpenApiParameter(name="invite_id", description="초대 ID", required=True, type=int)
        ],
        tags=["Refrigerators"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["accepted", "declined"], "example": "accepted"}
                },
                "required": ["status"]
            }
        },
        responses={
            200: {"description": "Invitation accepted or declined."},
            400: {"description": "Invalid status."},
            404: {"description": "Invitation not found."},
        }
    )
    def patch(self, request, invite_id):
        invite = get_object_or_404(RefrigeratorInvitation, pk=invite_id, invited_user=request.user)
        status_value = request.data.get('status')

        if status_value not in ['accepted', 'declined']:
            return Response({"error": "Invalid status."}, status=400)

        invite.status = status_value
        invite.save()

        if status_value == 'accepted':
            RefrigeratorAccess.objects.create(
                user=request.user,
                refrigerator=invite.refrigerator,
                role='member'
            )
            return Response({"message": "Invitation accepted. Access granted to refrigerator."}, status=200)

        return Response({"message": "Invitation declined."}, status=200)


class InvitationListView(APIView):
    """
    초대 목록 조회
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="초대 목록 조회",
        description="사용자가 받은 초대 및 보낸 초대 목록을 조회합니다.",
        tags=["Refrigerators"],
        responses={
            200: {
                "description": "초대 목록 조회 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "received_invitations": [
                                {
                                    "id": 1,
                                    "refrigerator_name": "Family Fridge",
                                    "status": "pending"
                                }
                            ],
                            "sent_invitations": [
                                {
                                    "id": 2,
                                    "refrigerator_name": "Office Fridge",
                                    "status": "accepted"
                                }
                            ]
                        }
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
                {
                    "id": invitation.id,
                    "refrigerator_name": invitation.refrigerator.name,
                    "status": invitation.status
                }
                for invitation in received_invitations
            ],
            "sent_invitations": [
                {
                    "id": invitation.id,
                    "refrigerator_name": invitation.refrigerator.name,
                    "status": invitation.status
                }
                for invitation in sent_invitations
            ],
        }

        return Response(data, status=200)