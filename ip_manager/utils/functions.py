import ipaddress

from django.conf import settings

from ip_manager import models


def add_initial_sources():
    sources = [
        (source, settings.CRAWL_SOURCES[source]["main"])
        for source in settings.CRAWL_SOURCES.keys()
    ]
    for source in sources:
        models.SourcePool.objects.get_or_create(name=source[0], url=source[1])


def get_ipv6_range(ip):
    ip_obj = ipaddress.ip_address(ip)
    ip_ranges = models.IpRange.objects.filter(
        version=6,
    ).values("id", "ip_network", "ip_from", "ip_to")

    for ip_range in ip_ranges:
        if ip_range["ip_network"] is None:
            if int(ip_range["ip_from"]) <= int(ip_obj) <= int(ip_range["ip_to"]):
                return models.IpRange.objects.get(id=ip_range["id"])
        if ip_obj in ipaddress.ip_network(ip_range["ip_network"]):
            return models.IpRange.objects.get(id=ip_range["id"])
