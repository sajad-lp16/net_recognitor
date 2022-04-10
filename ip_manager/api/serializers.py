from rest_framework import serializers

from ip_manager import models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = (
            'name',
            'code'
        )


class ISPSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ISP
        fields = (
            'name',
            'description',
            'tags',
        )


class IpRangeSerializer(serializers.ModelSerializer):
    isp = ISPSerializer()
    country = CountrySerializer()

    class Meta:
        model = models.IpRange
        fields = (
            'isp',
            'source',
            'ip_network',
            'ip_from',
            'ip_to',
            'country',
            'organization',
            'address',
            'latitude',
            'longitude',
        )
