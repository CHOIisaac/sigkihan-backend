from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django의 기본 settings 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Celery 앱 생성
app = Celery('project')

# settings.py에서 'CELERY'로 시작하는 설정 읽기
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱 내의 tasks.py 자동 검색
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')