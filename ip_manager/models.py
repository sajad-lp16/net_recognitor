from django.db import models
from django.utils.translation import ugettext_lazy as _


class ISP(models.Model):
    name = models.CharField(
        _("name"),
        max_length=100,
        blank=True
    )
    description = models.CharField(
        _("description"),
        max_length=255,
        blank=True
    )
    tags = models.CharField(
        _("tags"),
        max_length=100,
        null=True,
        blank=True
    )
    is_enable = models.BooleanField(
        _("expire time"),
        default=True
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("create time")
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name=_("update time")
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ip_manager_isp"
        verbose_name = _("isp")
        verbose_name_plural = _("isps")


class SourcePool(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("create time")
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name=_("update time")
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ip_manager_source"
        verbose_name = _("source")
        verbose_name_plural = _("sources")


class Country(models.Model):
    name = models.CharField(
        _("name"),
        max_length=50,
        null=False
    )
    code = models.CharField(
        _("code"),
        max_length=5,
        null=True
    )
    create_time = models.DateTimeField(
        _("create time"),
        auto_now_add=True
    )
    update_time = models.DateTimeField(
        _("update time"),
        auto_now=True
    )


class IpRange(models.Model):
    isp = models.ForeignKey(
        to=ISP,
        verbose_name=_("ISP"),
        on_delete=models.CASCADE
    )
    source = models.ForeignKey(
        to=SourcePool,
        on_delete=models.CASCADE,
        verbose_name=_("isp")
    )
    ip_network = models.CharField(
        max_length=30,
        verbose_name=_("ip network"),
        null=True,
        blank=True
    )
    ip_from = models.PositiveIntegerField(
        _("ip from"),
        db_index=True,
        null=True,
        blank=True
    )
    ip_to = models.PositiveIntegerField(
        _("ip to"),
        db_index=True,
        null=True,
        blank=True
    )
    is_enable = models.BooleanField(
        _("is enable"),
        default=True
    )
    expire_date = models.DateTimeField(
        _("expire time"),
        null=True, blank=True
    )
    country = models.ForeignKey(
        to=Country,
        on_delete=models.CASCADE,
        verbose_name=_("country"),
        null=True,
        blank=True,
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("organization")
    )
    address = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name=_("address")
    )
    latitude = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        blank=True,
        verbose_name=_("latitude")
    )
    longitude = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        blank=True,
        verbose_name=_("longitude")
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("create time")
    )
    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name=_("update time")
    )

    class Meta:
        db_table = "ip_manager_ip_ranges"
        verbose_name = _("ip_range")
        verbose_name_plural = _("ip_ranges")
