from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django 설정 파일을 Celery에 알려줍니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigkihan.settings')

app = Celery('sigkihan')

# Django 설정 파일의 CELERY 관련 설정을 가져옵니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱의 task를 자동으로 찾아서 로드합니다.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')