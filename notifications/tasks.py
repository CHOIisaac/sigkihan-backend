from django.utils.timezone import now
from datetime import timedelta
from foods.models import FridgeFood
from foods.utils import create_notification_for_refrigerator_users

def schedule_notifications():
    today = now().date()
    three_days_later = today + timedelta(days=3)
    d_day = today

    # D-3 알림 생성
    d3_foods = FridgeFood.objects.filter(expiration_date=three_days_later)
    for food in d3_foods:
        message = f"D-3 알림: '{food.default_food.name if food.default_food else food.name}'의 소비기한이 임박했습니다!"
        create_notification_for_refrigerator_users(food.refrigerator, message)

    # D-0 알림 생성
    d0_foods = FridgeFood.objects.filter(expiration_date=d_day)
    for food in d0_foods:
        message = f"D-0 알림: '{food.default_food.name if food.default_food else food.name}'의 소비기한이 오늘까지입니다!"
        create_notification_for_refrigerator_users(food.refrigerator, message)