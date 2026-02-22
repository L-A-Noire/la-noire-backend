from django.contrib import admin
from reward.models.payment import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reward",
        "processed_by",
        "processed_at",
        "recipient_full_name",
        "recipient_national_id",
        "payment_reference",
    )
    list_filter = ("processed_at",)
    search_fields = (
        "recipient_national_id",
        "recipient_full_name",
        "payment_reference",
        "processed_by__username",
        "reward__unique_code",
    )
    readonly_fields = ("processed_at",)
