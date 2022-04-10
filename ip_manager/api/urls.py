from django.urls import path

from . import views

app_name = "ip_manager_api"

urlpatterns = [
    path('', views.IpDataAPI.as_view(), name='ip_data'),
]
