from django.contrib import admin

from .models import AuditLog, Incident, Intervention


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "equipment", "priority", "status", "technician", "operator")
    list_filter = ("status", "priority", "criticality")
    search_fields = ("code", "title", "description", "equipment__name")


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ("code", "equipment", "technician", "intervention_type", "status", "start_date", "end_date")
    list_filter = ("status", "intervention_type", "priority")
    search_fields = ("code", "description", "equipment__name", "technician__full_name")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "model_name", "object_id", "user", "created_at")
    list_filter = ("action", "model_name")
    search_fields = ("object_id", "model_name", "user__email")
