from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    # def ready(self):
    #     # 스케줄러 시작
    #     from .tasks import start_scheduler
    #     start_scheduler()