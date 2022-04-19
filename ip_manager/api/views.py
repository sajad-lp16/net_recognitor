import ipaddress

from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import IntegerField
from django.db.models.functions import Cast

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response

from ip_manager.utils.mapper import CRAWLERS_MAPPER
from ip_manager.utils.functions import get_ipv6_range
from .serializers import IpRangeSerializer
from ip_manager import models


class IpDataAPI(views.APIView):
    serializer_class = IpRangeSerializer

    def get(self, request):
        source = request.query_params.get("source")
        if source not in settings.CRAWL_SOURCES.keys():
            source = settings.DEFAULT_SOURCE
        ip = request.query_params.get("ip") or None
        try:
            ip_type = ipaddress.ip_address(ip)
            int_ip = int(ip_type)
            is_ipv6 = ip_type.__class__.__name__ == "IPv6Address"
        except (ValueError, TypeError):
            return Response(
                {"details": _("Invalid ip address")}, status=status.HTTP_400_BAD_REQUEST
            )
        if not is_ipv6:
            ip_range = (
                models.IpRange.objects.annotate(
                    int_ip_from=Cast("ip_from", output_field=IntegerField()),
                    int_ip_to=Cast("ip_to", output_field=IntegerField()),
                )
                .filter(
                    source__name=source.casefold(),
                    expire_date__gte=timezone.now(),
                    int_ip_from__lte=int_ip,
                    int_ip_to__gte=int_ip,
                )
                .first()
            )
        else:
            ip_range = get_ipv6_range(ip)
        if ip_range is not None:
            return Response(
                self.serializer_class(ip_range).data, status=status.HTTP_200_OK
            )

        crawler = CRAWLERS_MAPPER.get(source.casefold())
        try:
            instance = crawler(ip)
            assert instance is not None
            return Response(
                self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {"detail": _("service is unavailable or source doesnt support ipv6")},
                status.HTTP_404_NOT_FOUND,
            )
