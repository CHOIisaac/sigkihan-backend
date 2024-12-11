from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import DefaultFood, FridgeFood, FoodHistory


class DefaultFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultFood
        fields = ['id', 'name', 'image']


class FridgeFoodSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    default_food_name = serializers.CharField(source="default_food.name", read_only=True)
    class Meta:
        model = FridgeFood
        fields = ['id', 'name', 'default_food_name', 'purchase_date', 'expiration_date', 'quantity']

    @extend_schema_field(serializers.CharField)
    def get_name(self, obj) -> str:
        return obj.default_food.name if obj.default_food else obj.name


class FoodHistorySerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=FoodHistory.ACTION_CHOICES)
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = FoodHistory
        fields = ['action', 'quantity', 'timestamp']