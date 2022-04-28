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
from ip_manager.utils.functions import get_ipv6_range, get_ip_version
from .serializers import IpRangeSerializer
from ip_manager import models


class IpDataAPI(views.APIView):

    __INVALID_IP_ERROR_MESSAGE = _("Invalid ip address")
    __SERVICE_ERROR = _("Service is Unavailable now")

    serializer_class = IpRangeSerializer

    def get(self, request):
        source = request.query_params.get("source")
        if source not in settings.CRAWL_SOURCES.keys():
            source = settings.DEFAULT_SOURCE
        ip = request.query_params.get("ip") or None
        int_ip, ip_version = get_ip_version(ip)
        if int_ip is None or ip_version is None:
            return Response(
                {"details": _("Invalid ip address")}, status=status.HTTP_400_BAD_REQUEST
            )
        if ip_version == 4:
            ip_range = (
                models.IpRange.objects.annotate(
                    int_ip_from=Cast("ip_from", output_field=IntegerField()),
                    int_ip_to=Cast("ip_to", output_field=IntegerField()),
                )
                .filter(
                    source__name=source.casefold(),
                    # expire_date__gte=timezone.now(),
                    int_ip_from__lte=int_ip,
                    int_ip_to__gte=int_ip,
                )
                .first()
            )
        else:
            self.__SERVICE_ERROR = _(
                str(self.__SERVICE_ERROR) + " Or Source Doesnt Support IPV6"
            )
            ip_range = get_ipv6_range(ip, source)
        if ip_range is not None and ip_range.expire_date >= timezone.now():
            return Response(
                self.serializer_class(ip_range).data, status=status.HTTP_200_OK
            )

        crawler = CRAWLERS_MAPPER.get(source.casefold())
        try:
            instance = crawler(ip)
            if ip_range is None:
                assert instance is not None
            if instance is None:
                return Response(
                    self.serializer_class(ip_range).data, status=status.HTTP_200_OK
                )
            return Response(
                self.serializer_class(instance).data, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {"detail": self.__SERVICE_ERROR},
                status.HTTP_404_NOT_FOUND,
            )
