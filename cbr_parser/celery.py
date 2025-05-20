#from __future__ import absolute_import
from eventlet import monkey_patch
monkey_patch()

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cbr_parser.settings')
app = Celery('cbr_parser')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
