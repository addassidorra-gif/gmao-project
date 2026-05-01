from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import EquipementViewSet


router = DefaultRouter()
router.register(r"equipements", EquipementViewSet, basename="equipements")

urlpatterns = [
    path("", include(router.urls)),
]
