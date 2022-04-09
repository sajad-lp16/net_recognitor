from django.urls import path, include

app_name = "ip_manager"

urlpatterns = [
    path("api/", include("ip_manager.api.urls", namespace="ip_manager_api")),
]
