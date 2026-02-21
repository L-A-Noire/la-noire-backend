from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user.models.user import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "national_id",
        "phone",
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Extra Fields",
            {
                "fields": (
                    "role",
                    "national_id",
                    "phone",
                )
            },
        ),
    )
