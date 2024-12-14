from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    fridge_food_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'fridge_food_name', 'message', 'd_day', 'is_read', 'created_at']

    def get_fridge_food_name(self, obj):
        return obj.fridge_food.name or obj.fridge_food.default_food.name