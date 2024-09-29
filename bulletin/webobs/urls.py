from django.urls import path

from . import views

urlpatterns = [
    path("webobs/", views.WebObsEndpoint.as_view(), name="bulletin-api-v1-webobs"),
]
