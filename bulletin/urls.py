from django.urls import include, path

from bulletin.api.endpoints.home_endpoint import HomeEndpoint

urlpatterns = [
    path("", HomeEndpoint.as_view(), name="home"),
    path("api/", include("bulletin.api.urls")),
]
