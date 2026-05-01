from django.urls import path

from .views import (
    EquipementCreateView,
    EquipementDeleteView,
    EquipementListView,
    EquipementUpdateView,
    export_equipements_csv,
)


app_name = "equipment"

urlpatterns = [
    path("equipements/", EquipementListView.as_view(), name="list"),
    path("equipements/ajouter/", EquipementCreateView.as_view(), name="create"),
    path("equipements/<int:pk>/modifier/", EquipementUpdateView.as_view(), name="update"),
    path("equipements/<int:pk>/supprimer/", EquipementDeleteView.as_view(), name="delete"),
    path("equipements/export/csv/", export_equipements_csv, name="export_csv"),
]
