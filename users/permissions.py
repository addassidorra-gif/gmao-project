from rest_framework.permissions import SAFE_METHODS, BasePermission


def has_role(user, roles):
    return user.is_authenticated and user.role in roles


def has_role_at_least(user, role):
    return user.is_authenticated and getattr(user, "has_role_at_least", lambda _: False)(role)


class UserManagementPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return has_role(request.user, ["admin"])


class EquipmentPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role == "admin"


class IncidentPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "admin":
            return request.method in SAFE_METHODS

        if request.user.role == "responsable":
            if request.method in SAFE_METHODS:
                return True
            return view.action in ["update", "partial_update"]

        if request.user.role == "operateur":
            return view.action in ["list", "retrieve", "create"]

        if request.user.role == "technicien":
            return False

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in ["admin", "responsable"]:
            return True

        if request.user.role == "operateur":
            return obj.operator_id == request.user.id

        if request.user.role == "technicien":
            return obj.technician_id == request.user.id

        return False


class InterventionPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == "admin":
            return request.method in SAFE_METHODS

        if request.user.role == "responsable":
            if request.method in SAFE_METHODS:
                return True
            return view.action in ["create", "update", "partial_update"]

        if request.user.role == "technicien":
            return view.action in ["list", "retrieve", "update", "partial_update"]

        if request.user.role == "operateur":
            return False

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in ["admin", "responsable"]:
            return True

        if request.user.role == "technicien":
            return obj.technician_id == request.user.id

        if request.user.role == "operateur":
            return obj.incident and obj.incident.operator_id == request.user.id

        return False


class AuditLogPermission(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, ["admin"])
