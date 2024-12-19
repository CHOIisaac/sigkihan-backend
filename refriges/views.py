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


class RefrigeratorInviteResponseView(APIView):
    permission_classes = [IsAuthenticated]

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