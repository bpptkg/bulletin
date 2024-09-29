from django.urls import include, path

from .endpoints.api_v1_endpoint import APIv1Endpoint

urlpatterns = [
    path("v1/", APIv1Endpoint.as_view(), name="bulletin-api-v1"),
    path("v1/", include("bulletin.webobs.urls")),
]
