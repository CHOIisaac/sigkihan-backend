from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import DefaultFood, FridgeFood, FoodHistory


class DefaultFoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultFood
        fields = ['id', 'name', 'image']


class FridgeFoodSerializer(serializers.ModelSerializer):
    # name = serializers.SerializerMethodField()
    default_food_name = serializers.CharField(source="default_food.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    storage_type_display = serializers.CharField(
        source='get_storage_type_display',
        read_only=True
    )

    class Meta:
        model = FridgeFood
        fields = ['id', 'name', 'default_food_name', 'storage_type', 'storage_type_display', 'purchase_date', 'expiration_date', 'quantity', 'image_url']

    # @extend_schema_field(serializers.CharField)
    # def get_name(self, obj) -> str:
    #     return obj.default_food.name if obj.default_food else obj.name

    def get_image_url(self, obj) -> str:
        if obj.default_food and obj.default_food.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.default_food.image.url)
        return None


class FoodHistorySerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=FoodHistory.ACTION_CHOICES)
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = FoodHistory
        fields = ['action', 'quantity', 'timestamp']
