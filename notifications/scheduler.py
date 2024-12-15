from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from django.utils.timezone import now
from pytz import timezone

from foods.models import FridgeFood
from sigkihan import settings
from .models import Notification
from refriges.models import RefrigeratorAccess
from datetime import timedelta, date

logger = logging.getLogger(__name__)

korea_tz = timezone('Asia/Seoul')
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
    # 개발 환경에서만 스케줄러 실행
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_notifications, CronTrigger(hour=0, minute=15), id="daily_notifications", replace_existing=True)
    scheduler.start()
    print("Scheduler started.")