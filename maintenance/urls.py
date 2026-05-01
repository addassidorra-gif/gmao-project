from django.urls import path

from .views import (
    AuditLogListView,
    DashboardView,
    FrontendAppView,
    HomeRedirectView,
    IncidentCreateView,
    IncidentDeleteView,
    IncidentListView,
    IncidentUpdateView,
    InterventionCreateView,
    InterventionDeleteView,
    InterventionListView,
    InterventionUpdateView,
    export_incidents_csv,
    export_interventions_csv,
)


app_name = "maintenance"

urlpatterns = [
    path("", FrontendAppView.as_view(), name="home"),
    path("app/", FrontendAppView.as_view(), name="spa"),
    path("legacy/", HomeRedirectView.as_view(), name="legacy_home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("pannes/", IncidentListView.as_view(), name="incident_list"),
    path("pannes/ajouter/", IncidentCreateView.as_view(), name="incident_create"),
    path("pannes/<int:pk>/modifier/", IncidentUpdateView.as_view(), name="incident_update"),
    path("pannes/<int:pk>/supprimer/", IncidentDeleteView.as_view(), name="incident_delete"),
    path("pannes/export/csv/", export_incidents_csv, name="incident_export_csv"),
    path("interventions/", InterventionListView.as_view(), name="intervention_list"),
    path("interventions/ajouter/", InterventionCreateView.as_view(), name="intervention_create"),
    path("interventions/<int:pk>/modifier/", InterventionUpdateView.as_view(), name="intervention_update"),
    path("interventions/<int:pk>/supprimer/", InterventionDeleteView.as_view(), name="intervention_delete"),
    path("interventions/export/csv/", export_interventions_csv, name="intervention_export_csv"),
    path("audit-logs/", AuditLogListView.as_view(), name="audit_logs"),
]
