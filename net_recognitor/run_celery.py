from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "net_recognitor.settings")
app = Celery("net_recognitor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(related_name="main_crawlers")
