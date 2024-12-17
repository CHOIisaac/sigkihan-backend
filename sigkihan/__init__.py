from __future__ import absolute_import, unicode_literals

# Celery를 프로젝트에 포함
from .celery_app import app as celery_app

__all__ = ('celery_app',)