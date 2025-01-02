from datetime import timedelta, date

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from foods.models import FridgeFood
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from refriges.models import RefrigeratorAccess


class NotificationListView(APIView):
    """
    특정 냉장고의 알림 조회
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="냉장고 식품 알림 조회",
        description="특정 냉장고와 연결된 사용자들의 모든 알림을 조회합니다. 7일 이내의 읽지 않은 알림만 반환합니다.",
        tags=["Notifications"],
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request, refrigerator_id):
        one_week_ago = now() - timedelta(days=7)

        # 특정 냉장고와 연결된 모든 사용자들의 알림 조회
        notifications = Notification.objects.filter(
            refrigerator_id=refrigerator_id,
            created_at__gte=one_week_ago,
            d_day='D-3'
            # is_read=False
        ).order_by('-created_at')

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=200)


class PopupNotificationListView(APIView):
    """
    팝업 알림 조회
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="팝업 식품 알림 조회",
        description="특정 냉장고와 연결된 사용자들의 모든 알림을 조회합니다.",
        tags=["Notifications"],
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request, refrigerator_id):

        # 특정 냉장고와 연결된 모든 사용자들의 알림 조회
        notifications = Notification.objects.filter(
            refrigerator_id=refrigerator_id,
            d_day='D-0',
            is_read=False
        )

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=200)


class NotificationMarkAsReadView(APIView):
    """
    알림 읽음 처리
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="냉장고 식품 알림 읽음 처리",
        description="특정 냉장고의 알림을 읽음 상태로 변경합니다.",
        tags=["Notifications"],
        responses={
            200: {"description": "알림 읽음 처리 성공"},
            404: {"description": "알림을 찾을 수 없음"}
        },
    )
    def post(self, request, refrigerator_id):
        notifications = Notification.objects.filter(refrigerator_id=refrigerator_id, is_read=False, d_day='D-3')

        if not notifications.exists():
            return Response({"error": "No unread notifications found for this refrigerator."}, status=404)

        # 알림 읽음 상태로 변경
        notifications.update(is_read=True)
        return Response({"message": "All unread notifications marked as read."}, status=200)


class PopupNotificationMarkAsReadView(APIView):
    """
    알림 읽음 처리
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="냉장고 식품 팝업 알림 읽음 처리",
        description="특정 냉장고의 알림을 읽음 상태로 변경합니다.",
        tags=["Notifications"],
        responses={
            200: {"description": "알림 읽음 처리 성공"},
            404: {"description": "알림을 찾을 수 없음"}
        },
    )
    def post(self, request, refrigerator_id):
        notifications = Notification.objects.filter(refrigerator_id=refrigerator_id, is_read=False, d_day='D-0')

        if not notifications.exists():
            return Response({"error": "No unread notifications found for this refrigerator."}, status=404)

        # 알림 읽음 상태로 변경
        notifications.update(is_read=True)
        return Response({"message": "All unread notifications marked as read."}, status=200)


class CreateNotificationAPIView(APIView):
    """
    특정 냉장고와 연결된 모든 사용자에게 알림 생성
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="냉장고 식품 알림 생성",
        description="특정 냉장고에 연결된 모든 사용자에게 알림을 생성합니다.",
        tags=["Notifications"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "소비기한 임박 알림", "description": "알림 메시지"},
                    "d_day": {"type": "string", "example": "D-3", "description": "디데이 정보"}
                },
                "required": ["message", "d_day"]
            }
        },
        responses={201: {"description": "알림 생성 성공"}},
    )
    def post(self, request, refrigerator_id):

        today = date.today()
        # D-3 알림 생성
        d_3_date = today + timedelta(days=3)
        foods_d_3 = FridgeFood.objects.filter(expiration_date=d_3_date)
        for food in foods_d_3:
            users = RefrigeratorAccess.objects.filter(refrigerator=refrigerator_id).values_list('user', flat=True)
            for user_id in users:
                Notification.objects.create(
                    user_id=user_id,
                    refrigerator=food.refrigerator,
                    message=food.default_food.comment,
                    d_day="D-3"
                )
        return Response({"message": "Notifications created for all users."}, status=201)


class CreatePopupNotificationAPIView(APIView):
    """
    특정 냉장고와 연결된 모든 사용자에게 알림 생성
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="냉장고 팝업 알림 생성",
        description="특정 냉장고에 연결된 모든 사용자에게 알림을 생성합니다.",
        tags=["Notifications"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "소비기한 임박 알림", "description": "알림 메시지"},
                    "d_day": {"type": "string", "example": "D-0", "description": "디데이 정보"}
                },
                "required": ["message", "d_day"]
            }
        },
        responses={201: {"description": "알림 생성 성공"}},
    )
    def post(self, request, refrigerator_id):

        today = date.today()
        # D-0 알림 생성
        foods_d_0 = FridgeFood.objects.filter(expiration_date=today)
        print(foods_d_0)
        for food in foods_d_0:
            food_name = food.name
            users = RefrigeratorAccess.objects.filter(refrigerator=refrigerator_id).values_list('user', flat=True)
            for user_id in users:
                Notification.objects.create(
                    user_id=user_id,
                    refrigerator=food.refrigerator,
                    message=food_name,
                    d_day="D-0"
                )
        return Response({"message": "Notifications created for all users."}, status=201)