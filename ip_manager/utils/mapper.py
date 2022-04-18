from functools import partial
from ip_manager.crawlers import main_crawlers

CRAWLERS_MAPPER = {
    "default": partial(main_crawlers.crawl_ip_info),
    "ipinfo": partial(main_crawlers.crawl_ip_info),
    "ipdata": partial(main_crawlers.crawl_ip_data),
    "myip": partial(main_crawlers.crawl_my_ip),
    "ripe": partial(main_crawlers.crawl_ripe),
}
