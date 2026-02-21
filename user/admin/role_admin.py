from django.contrib import admin
from user.models.role import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
    )
    search_fields = ("title",)
