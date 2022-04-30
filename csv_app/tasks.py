import csv
from io import StringIO
from itertools import chain

from threading import Thread
from celery import shared_task

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

    ip_info_task = Thread(
        target=main_crawlers.crawl_ip_info, args=[csv_data], kwargs={"many": True}
    )
    my_ip_task = Thread(
        target=main_crawlers.crawl_my_ip, args=[csv_data], kwargs={"many": True}
    )
    ripe_task = Thread(
        target=main_crawlers.crawl_ripe, args=[csv_data], kwargs={"many": True}
    )
    ip_data_task = Thread(
        target=main_crawlers.crawl_ip_data, args=[csv_data], kwargs={"many": True}
    )

    ip_info_task.start()
    my_ip_task.start()
    ripe_task.start()
    ip_data_task.start()

    ip_info_task.join()
    my_ip_task.join()
    ripe_task.join()
    ip_data_task.join()

    obj.delete()
