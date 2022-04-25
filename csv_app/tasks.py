import csv
from io import StringIO
import time
from itertools import chain

from celery import shared_task

from ip_manager.tasks import insert_ip_data
from ip_manager.crawlers import main_crawlers

from . import models


@shared_task
def add_ips(create_time):
    try:
        obj = models.CsvFile.objects.get(create_time=create_time)
    except models.CsvFile.DoesNotExist:
        return
    data = obj.csv_file.file.read().decode("utf-8")
    csv_file = csv.reader(StringIO(data))
    csv_data = list(filter(lambda x: bool(x), list(chain(*csv_file))))
    # main_crawlers.crawl_ip_info.delay(csv_data, many=True)
    main_crawlers.crawl_ripe(csv_data, many=True)
    # main_crawlers.crawl_ip_data.delay(csv_data, many=True)
    # main_crawlers.crawl_my_ip.delay(csv_data, many=True)
