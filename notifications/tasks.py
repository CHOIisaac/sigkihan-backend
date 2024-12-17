from apscheduler.schedulers.background import BackgroundScheduler
import logging

from celery.app import shared_task
from pytz import timezone

from foods.models import FridgeFood
from .models import Notification
from refriges.models import RefrigeratorAccess
from datetime import timedelta, date

logger = logging.getLogger(__name__)

korea_tz = timezone('Asia/Seoul')
@shared_task
def send_notifications():
    # D-3 알림 생성
    today = date.today()

    d_3_date = today + timedelta(days=3)
    foods_d_3 = FridgeFood.objects.filter(expiration_date=d_3_date)
    for food in foods_d_3:
        users = RefrigeratorAccess.objects.filter(refrigerator=food.refrigerator).values_list('user', flat=True)
        for user_id in users:
            Notification.objects.create(
                user_id=user_id,
                refrigerator=food.refrigerator,
                message=food.default_food.comment,
                d_day="D-3"
            )

    # D-0 알림 생성
    foods_d_0 = FridgeFood.objects.filter(expiration_date=today)
    for food in foods_d_0:
        food_name = food.name
        users = RefrigeratorAccess.objects.filter(refrigerator=food.refrigerator).values_list('user', flat=True)
        for user_id in users:
            Notification.objects.create(
                user_id=user_id,
                refrigerator=food.refrigerator,
                message=food_name,
                d_day="D-0"
            )

    logger.info("Notifications have been created for D-3 and D-0 foods.")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_notifications, 'interval', minutes=1, id="daily_notifications", replace_existing=True)
    scheduler.start()
    print("Scheduler started.")