from django.contrib import admin

from .models import Equipement


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "criticality", "location")
    list_filter = ("status", "criticality")
    search_fields = ("code", "name", "location", "reference")
