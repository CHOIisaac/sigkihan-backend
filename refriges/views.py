from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from refriges.models import RefrigeratorAccess, Refrigerator, RefrigeratorInvitation, RefrigeratorMemo
from refriges.serializers import RefrigeratorSerializer, RefrigeratorMemoSerializer, RefrigeratorInvitationSerializer
from refriges.services import create_invitation
from users.models import CustomUser


class RefrigeratorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="냉장고 목록 조회",
        description="현재 사용자가 접근 권한이 있는 모든 냉장고의 목록을 반환합니다.",
        tags=["Refrigerators"],
        responses={200: RefrigeratorSerializer(many=True)}
    )
    def list(self, request):
        """
        냉장고 목록 조회
        """
        refrigerators = Refrigerator.objects.filter(access_list__user=request.user).distinct()
        serializer = RefrigeratorSerializer(refrigerators, many=True)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="특정 냉장고 조회",
        description="냉장고 ID로 특정 냉장고의 상세 정보를 조회합니다.",
        tags=["Refrigerators"],
        responses={
            200: RefrigeratorSerializer,
            404: {"description": "냉장고를 찾을 수 없습니다."}
        }
    )
    def retrieve(self, request, pk=None):
        """
        특정 냉장고 조회
        """
        refrigerator = get_object_or_404(Refrigerator, id=pk, access_list__user=request.user)
        serializer = RefrigeratorSerializer(refrigerator)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="냉장고 생성",
        description="새로운 냉장고를 생성하고 요청 사용자에게 소유자 권한을 부여합니다.",
        tags=["Refrigerators"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refrigerator_name": {
                        "type": "string",
                        "example": "우리집 냉장고",
                        "description": "냉장고 이름"
                    },
                    "description": {
                        "type": "string",
                        "example": "집에서 사용하는 냉장고입니다.",
                        "description": "냉장고 설명 (선택사항)"
                    }
                },
                "required": ["refrigerator_name"]
            }
        },
        responses={
            201: RefrigeratorSerializer,
            400: OpenApiResponse(
                description="유효하지 않은 요청 데이터",
                examples=[
                    {
                        "error": "Refrigerator name is required."
                    }
                ]
            )
        }
    )
    def create(self, request):
        """
        냉장고 생성
        """
        user = request.user
        refrigerator_name = request.data.get('refrigerator_name')
        description = request.data.get('description')

        if not refrigerator_name:
            return Response({"error": "Refrigerator name is required."}, status=400)

        refrigerator = Refrigerator.objects.create(
            name=refrigerator_name,
            description=description
        )
        RefrigeratorAccess.objects.create(
            user=user,
            refrigerator=refrigerator,
            role='owner'
        )
        serializer = RefrigeratorSerializer(refrigerator)
        return Response(serializer.data, status=201)

    # @action(detail=True, methods=["get"])
    # @extend_schema(
    #     summary="특정 냉장고 사용자 목록",
    #     description="특정 냉장고에 접근 권한이 있는 사용자 목록을 반환합니다.",
    #     tags=["Refrigerators"],
    #     responses={200: "사용자 목록"}
    # )
    # def users(self, request, pk=None):
    #     """
    #     특정 냉장고 사용자 조회
    #     """
    #     refrigerator = get_object_or_404(Refrigerator, id=pk, access_list__user=request.user)
    #     users = refrigerator.access_list.all()
    #     user_data = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
    #     return Response(user_data, status=200)

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
        tags=["RefrigeratorInvitations"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "admin2@admin.com", "description": "초대할 사용자 ID"}
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
        invitee_email = request.data.get('email')
        if not invitee_email:
            return Response({"error": "이메일을 확인해주세요."}, status=400)

        # 냉장고 접근 확인
        refrigerator = get_object_or_404(Refrigerator, pk=refrigerator_id)
        if not RefrigeratorAccess.objects.filter(user=inviter, refrigerator=refrigerator, role='owner').exists():
            return Response({"error": "You are not the owner of this refrigerator."}, status=403)

        # 초대 생성
        invitation = create_invitation(inviter, invitee_email, refrigerator)
        return Response({"invitation_id": invitation.id, "message": "Invitation sent successfully."}, status=201)


class InvitationStatusUpdateView(APIView):
    """
    초대 상태 업데이트
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="초대 상태 업데이트",
        description="사용자가 받은 초대의 상태를 수락(accepted) 또는 거절(declined)로 변경합니다.",
        # parameters=[
        #     OpenApiParameter(name="invite_id", description="초대 ID", required=True, type=int)
        # ],
        tags=["RefrigeratorInvitations"],
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
        invite = get_object_or_404(RefrigeratorInvitation, pk=invite_id, invitee_email=request.user.email)
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
        description="사용자가 받은 초대 목록을 반환합니다. 초대 상태가 'pending'인 초대만 조회됩니다.",
        tags=["RefrigeratorInvitations"],
        responses={200: RefrigeratorInvitationSerializer(many=True)}
    )
    def get(self, request):
        user_email = request.user.email

        # 사용자의 이메일로 초대받은 초대 조회
        invitations = RefrigeratorInvitation.objects.filter(
            invitee_email=user_email,
            status='pending'  # 'pending' 상태의 초대만 반환
        ).order_by('-created_at')

        # 직렬화하여 반환
        serializer = RefrigeratorInvitationSerializer(invitations, many=True)
        return Response(serializer.data, status=200)


class Remove


class RefrigeratorMemoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="냉장고 메모 추가",
        description="특정 냉장고에 메모를 추가합니다.",
        tags=["RefrigeratorMemos"],
        # parameters=[
        #     OpenApiParameter(name="refrigerator_id", description="냉장고 ID", required=True, type=int)
        # ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "example": "Shopping List"},
                    "content": {"type": "string", "example": "Buy milk, eggs, and butter"}
                },
                "required": ["title", "content"]
            }
        },
        responses={201: RefrigeratorMemoSerializer}
    )
    def post(self, request, refrigerator_id):
        """
        특정 냉장고에 메모 추가
        """
        refrigerator = get_object_or_404(Refrigerator, id=refrigerator_id)

        # 냉장고 접근 권한 확인
        if not RefrigeratorAccess.objects.filter(user=request.user, refrigerator=refrigerator).exists():
            return Response({"error": "You do not have access to this refrigerator."}, status=403)

        title = request.data.get('title')
        content = request.data.get('content')

        if not title or not content:
            return Response({"error": "Title and content are required."}, status=400)

        memo = RefrigeratorMemo.objects.create(
            refrigerator=refrigerator,
            user=request.user,
            title=title,
            content=content
        )
        serializer = RefrigeratorMemoSerializer(memo)
        return Response(serializer.data, status=201)

    @extend_schema(
        summary="냉장고 메모 조회",
        description="특정 냉장고의 메모를 최신순으로 조회합니다.",
        tags=["RefrigeratorMemos"],
        responses={200: RefrigeratorMemoSerializer(many=True)}
    )
    def get(self, request, refrigerator_id):
        """
        특정 냉장고의 메모 조회
        """
        refrigerator = get_object_or_404(Refrigerator, id=refrigerator_id)

        # 냉장고 접근 권한 확인
        if not RefrigeratorAccess.objects.filter(user=request.user, refrigerator=refrigerator).exists():
            return Response({"error": "You do not have access to this refrigerator."}, status=403)

        memos = RefrigeratorMemo.objects.filter(refrigerator=refrigerator)
        serializer = RefrigeratorMemoSerializer(memos, many=True)
        return Response(serializer.data, status=200)


class RefrigeratorMemoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="메모 수정",
        description="사용자가 작성한 메모를 수정합니다.",
        tags=["RefrigeratorMemos"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "example": "Updated Shopping List"},
                    "content": {"type": "string", "example": "Buy milk, eggs, butter, and cheese"}
                }
            }
        },
        responses={200: RefrigeratorMemoSerializer}
    )
    def patch(self, request, refrigerator_id, memo_id):
        """
        메모 수정
        """
        memo = get_object_or_404(RefrigeratorMemo, id=memo_id, user=request.user, refrigerator_id=refrigerator_id)
        title = request.data.get('title', memo.title)
        content = request.data.get('content', memo.content)

        memo.title = title
        memo.content = content
        memo.save()

        serializer = RefrigeratorMemoSerializer(memo)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="메모 삭제",
        description="사용자가 작성한 메모를 삭제합니다.",
        tags=["RefrigeratorMemos"],
        responses={204: {"description": "메모 삭제 성공"}}
    )
    def delete(self, request, refrigerator_id, memo_id):
        """
        메모 삭제
        """
        memo = get_object_or_404(RefrigeratorMemo, id=memo_id, user=request.user, refrigerator_id=refrigerator_id)
        memo.delete()
        return Response({"message": "Memo deleted successfully."}, status=204)