from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AuditLog, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "role", "sector", "is_active", "is_staff")
    list_filter = ("role", "sector", "is_active")
    search_fields = ("email", "full_name")
    ordering = ("full_name",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Perfil", {"fields": ("full_name", "role", "sector")}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module", "description", "ip_address")
    list_filter = ("action", "module", "created_at")
    search_fields = ("user__email", "user__full_name", "description", "ip_address")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
