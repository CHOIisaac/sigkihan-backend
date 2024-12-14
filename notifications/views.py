from datetime import timedelta

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from refriges.models import RefrigeratorAccess


class NotificationListView(APIView):
    """
    특정 냉장고의 알림 조회
    """
    @extend_schema(
        summary="냉장고 알림 조회",
        description="특정 냉장고와 연결된 사용자들의 모든 알림을 조회합니다. 7일 이내의 읽지 않은 알림만 반환합니다.",
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request, refrigerator_id):
        one_week_ago = now() - timedelta(days=7)

        # 특정 냉장고와 연결된 모든 사용자들의 알림 조회
        notifications = Notification.objects.filter(
            refrigerator_id=refrigerator_id,
            created_at__gte=one_week_ago,
            is_read=False
        ).order_by('-created_at')

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=200)


class NotificationMarkAsReadView(APIView):
    """
    알림 읽음 처리
    """

    @extend_schema(
        summary="냉장고 알림 읽음 처리",
        description="특정 냉장고의 알림을 읽음 상태로 변경합니다.",
        responses={
            200: {"description": "알림 읽음 처리 성공"},
            404: {"description": "알림을 찾을 수 없음"}
        },
    )
    def post(self, request, refrigerator_id, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, refrigerator_id=refrigerator_id)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read."}, status=200)


class CreateNotificationAPIView(APIView):
    """
    특정 냉장고와 연결된 모든 사용자에게 알림 생성
    """
    def post(self, request, refrigerator_id):
        message = request.data.get('message')
        if not message:
            return Response({"error": "Message is required."}, status=400)

        # 냉장고와 연결된 모든 사용자 가져오기
        refrigerator_accesses = RefrigeratorAccess.objects.filter(refrigerator_id=refrigerator_id)
        if not refrigerator_accesses.exists():
            return Response({"error": "No users found for the specified refrigerator."}, status=404)

        # 알림 생성
        for access in refrigerator_accesses:
            Notification.objects.create(
                user=access.user,
                refrigerator_id=refrigerator_id,
                message=message,
            )

        return Response({"message": "Notifications created for all users."}, status=201)