from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("", include("equipment.urls")),
    path("", include("maintenance.urls")),
    path("api/", include("users.api_urls")),
    path("api/", include("equipment.api_urls")),
    path("api/", include("maintenance.api_urls")),
]
