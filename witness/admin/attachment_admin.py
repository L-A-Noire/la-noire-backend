from django.contrib import admin
from witness.models.attachment import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file",
        "provided_by",
    )
    search_fields = (
        "file",
        "provided_by__username",
    )
