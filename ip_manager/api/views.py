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

    __INVALID_IP_ERROR_MESSAGE = "Invalid Ip Address"
    __SERVICE_ERROR = "Service Is Unavailable Now"

    serializer_class = IpRangeSerializer

    def get(self, request):
        source = request.query_params.get("source")
        is_valid_source = source in settings.CRAWL_SOURCES.keys()
        ip = request.query_params.get("ip") or None
        int_ip, ip_version = get_ip_version(ip)

        if int_ip is None or ip_version is None:
            return Response(
                {"details": _("Invalid Ip Address")}, status=status.HTTP_400_BAD_REQUEST
            )
        if ip_version == 4:
            ip_range_que = models.IpRange.objects.annotate(
                int_ip_from=Cast("ip_from", output_field=IntegerField()),
                int_ip_to=Cast("ip_to", output_field=IntegerField()),
            ).filter(
                int_ip_from__lte=int_ip,
                int_ip_to__gte=int_ip,
            )
            if is_valid_source:
                ip_range_que.filter(
                    source__name=source.casefold()
                )
            ip_range = ip_range_que.first()
        else:
            self.__SERVICE_ERROR = (
                self.__SERVICE_ERROR + " Or Source Doesnt Support IPV6"
            )
            ip_range = get_ipv6_range(ip, source, is_valid_source)

        if not is_valid_source:
            source = settings.DEFAULT_SOURCE

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
                {"detail": _(self.__SERVICE_ERROR)},
                status.HTTP_404_NOT_FOUND,
            )
