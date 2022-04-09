import csv
from io import StringIO
import time

from celery import shared_task

from ip_manager.tasks import insert_ip_data
from . import models


@shared_task
def add_ips(create_time):
    try:
        obj = models.CsvFile.objects.get(create_time=create_time)
    except models.CsvFile.DoesNotExist:
        return
    data = obj.csv_file.file.read().decode("utf-8")
    csv_file = csv.reader(StringIO(data), delimiter=",", quotechar="'")
    for ip_list in csv_file:
        for ip in ip_list:
            if ip:
                insert_ip_data(ip)
                time.sleep(2)
    obj.delete()
