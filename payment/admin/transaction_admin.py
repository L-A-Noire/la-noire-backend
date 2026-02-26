from django.contrib import admin

from payment.models.transaction import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "factor_id",
        "trans_id",
        "amount",
        "mobile_num",
        "is_success",
        "is_used",
        "created_at",
    )
    list_filter = (
        "is_success",
        "is_used",
        "created_at",
    )
    search_fields = (
        "factor_id",
        "trans_id",
        "id_get",
        "mobile_num",
        "card_number",
    )
    readonly_fields = (
        "factor_id",
        "trans_id",
        "id_get",
        "card_number",
        "created_at",
        "updated_at",
    )
