from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import AuditLogViewSet, IncidentViewSet, InterventionViewSet


router = DefaultRouter()
router.register(r"incidents", IncidentViewSet, basename="incidents")
router.register(r"interventions", InterventionViewSet, basename="interventions")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-logs")

urlpatterns = [
    path("", include(router.urls)),
]
