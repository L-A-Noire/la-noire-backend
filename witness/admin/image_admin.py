from django.contrib import admin
from witness.models.image import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image",
        "uploaded_by",
    )
    search_fields = ("uploaded_by__username",)
