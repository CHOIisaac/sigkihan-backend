from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

from foods.models import FridgeFood, FoodHistory


@receiver(pre_delete, sender=FridgeFood)
def create_food_history_on_delete(sender, instance, **kwargs):
    FoodHistory.objects.create(
        fridge_food_name=instance.name or instance.default_food.name,
        fridge_food_id=instance.id,
        user=instance.refrigerator.access_list.first().user,  # 첫 사용자 참조
        action='discarded',
        quantity=instance.quantity
    )