from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.serializers import NotificationSerializer


# Create your views here.
# class NotificationListView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     @extend_schema(
#         summary="특정 냉장고 알림 조회",
#         description="특정 냉장고에 대한 모든 알림을 조회합니다.",
#         parameters=[
#             {"name": "refrigerator_id", "in": "path", "required": True, "description": "냉장고 ID",
#              "schema": {"type": "integer"}}
#         ],
#         responses={200: NotificationSerializer(many=True)}
#     )