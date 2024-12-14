from pytz import timezone
from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'message', 'd_day', 'is_read', 'created_at']

    def get_created_at(self, obj):
        # UTC 시간에서 한국 시간대로 변환
        korea_time = obj.created_at.astimezone(timezone('Asia/Seoul'))
        return korea_time.strftime('%Y-%m-%d %H:%M:%S')