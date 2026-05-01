from rest_framework import viewsets

from maintenance.utils import create_audit_log
from users.permissions import EquipmentPermission

from .models import Equipement
from .serializers import EquipementSerializer


class EquipementViewSet(viewsets.ModelViewSet):
    queryset = Equipement.objects.all()
    serializer_class = EquipementSerializer
    permission_classes = [EquipmentPermission]

    def perform_create(self, serializer):
        equipement = serializer.save()
        create_audit_log(
            user=self.request.user,
            action="create",
            model_name="Equipement",
            object_id=equipement.pk,
            details={"code": equipement.code, "name": equipement.name},
        )

    def perform_update(self, serializer):
        equipement = serializer.save()
        create_audit_log(
            user=self.request.user,
            action="update",
            model_name="Equipement",
            object_id=equipement.pk,
            details={"code": equipement.code, "name": equipement.name},
        )

    def perform_destroy(self, instance):
        create_audit_log(
            user=self.request.user,
            action="delete",
            model_name="Equipement",
            object_id=instance.pk,
            details={"code": instance.code, "name": instance.name},
        )
        instance.delete()
