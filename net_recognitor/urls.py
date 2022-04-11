from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("ip_manager.urls", namespace="ip_manager")),
    path("admin/", admin.site.urls),
]

admin.site.site_header = "NetRecognitor"
admin.site.site_title = "NetRecognitor"
admin.site.index_title = "NetRecognitor"
