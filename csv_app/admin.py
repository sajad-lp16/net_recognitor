from django.contrib import admin

from . import models


@admin.register(models.CsvFile)
class CsvAdmin(admin.ModelAdmin):
    pass
