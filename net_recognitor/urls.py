from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("ip_manager.urls", namespace="ip_manager")),
    path("admin/", admin.site.urls),
]
