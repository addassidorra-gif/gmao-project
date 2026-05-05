from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "email", "full_name", "role", "approval_status", "is_active", "is_staff")
    list_filter = ("role", "approval_status", "is_active", "is_staff", "is_superuser")
    ordering = ("email",)
    search_fields = ("email", "full_name")
    actions = ("approve_users", "reject_users")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations", {"fields": ("full_name", "role", "approval_status")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "role", "approval_status", "password1", "password2", "is_active", "is_staff"),
            },
        ),
    )

    @admin.action(description="Accepter les comptes sélectionnés")
    def approve_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(
            approval_status=User.ApprovalStatus.ACCEPTED,
            is_active=True,
        )
        self.message_user(request, f"{updated} compte(s) accepté(s).")

    @admin.action(description="Refuser les comptes sélectionnés")
    def reject_users(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(
            approval_status=User.ApprovalStatus.REJECTED,
            is_active=False,
        )
        self.message_user(request, f"{updated} compte(s) refusé(s).")
