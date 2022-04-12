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
from .serializers import IpRangeSerializer
from ip_manager import models


class IpDataAPI(views.APIView):
    serializer_class = IpRangeSerializer

    def get(self, request):
        source = request.query_params.get("source") or settings.DEFAULT_SOURCE
        ip = request.query_params.get("ip") or None
        try:
            int_ip = int(ipaddress.ip_address(ip))
        except (ValueError, TypeError):
            return Response(
                {"details": _("Invalid ip address")}, status=status.HTTP_400_BAD_REQUEST
            )
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
        if ip_range is not None:
            return Response(
                self.serializer_class(ip_range).data, status=status.HTTP_200_OK
            )
        crawler = CRAWLERS_MAPPER.get(source.casefold())
        try:
            return Response(
                self.serializer_class(crawler(ip)).data, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {
                    "detail": _("service is unavailable now."),
                    status: status.HTTP_404_NOT_FOUND,
                }
            )
