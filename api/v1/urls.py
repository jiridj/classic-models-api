from django.urls import include, path

from .classicmodels.urls import urlpatterns as classicmodels_urls


urlpatterns = [
    path("classicmodels/", include((classicmodels_urls, "classicmodels"), namespace="classicmodels")),
]


