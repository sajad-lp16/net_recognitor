import ipaddress

from django.conf import settings
from django.utils import timezone

from ip_manager import models


def add_initial_sources():
    sources = [
        (source, settings.CRAWL_SOURCES[source]["main"])
        for source in settings.CRAWL_SOURCES.keys()
    ]
    for source in sources:
        models.SourcePool.objects.get_or_create(name=source[0], url=source[1])


def get_ipv6_range(ip, source, is_valid_source):
    ip_obj = ipaddress.ip_address(ip)
    if is_valid_source:
        ip_ranges = models.IpRange.objects.filter(
            version=6,
            source__name=source.casefold()
        ).exclude(
            ip_from__isnull=True,
            ip_to__isnull=True,
            ip_network__isnull=True,
            expire_date__lt=timezone.now(),
        ).values("id", "ip_network", "ip_from", "ip_to")
    else:
        ip_ranges = models.IpRange.objects.filter(
            version=6,
        ).exclude(
            ip_from__isnull=True,
            ip_to__isnull=True,
            ip_network__isnull=True,
        ).values("id", "ip_network", "ip_from", "ip_to")
    for ip_range in ip_ranges:
        if ip_range["ip_network"] is None:
            if int(ip_range["ip_from"]) <= int(ip_obj) <= int(ip_range["ip_to"]):
                return models.IpRange.objects.get(id=ip_range["id"])
        if ip_obj in ipaddress.ip_network(ip_range["ip_network"]):
            return models.IpRange.objects.get(id=ip_range["id"])
    return None


def get_ip_version(ip):
    try:
        ip_type = ipaddress.ip_address(ip)
        int_ip = int(ip_type)
        ip_version = 6 if ip_type.__class__.__name__ == "IPv6Address" else 4
        return int_ip, ip_version
    except (ValueError, TypeError):
        return None, None
