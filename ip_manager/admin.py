from django.contrib import admin

from . import models


@admin.register(models.IpRange)
class IpRangeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ISP)
class ISPAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SourcePool)
class SourcePoolAdmin(admin.ModelAdmin):
    pass
