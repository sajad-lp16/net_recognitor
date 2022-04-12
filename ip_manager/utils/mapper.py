from functools import partial
from ip_manager.crawlers import main_crawlers

CRAWLERS_MAPPER = {
    "default": partial(main_crawlers.crawl_ip_info),
    "ipinfo": partial(main_crawlers.crawl_ip_info),
    "ipregistry": partial(main_crawlers.crawl_ip_registry),
    "ipdata": partial(main_crawlers.crawl_ip_data),
    "ipdata_api": partial(main_crawlers.crawl_ip_data_api),
    "myip": partial(main_crawlers.crawl_myip),
    "ripe": partial(main_crawlers.crawl_ripe),
}
