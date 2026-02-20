from django.db import models


class Complaint(models.Model):
    COMPLAINT_STATUS = (
        ("pending_cadet", "Pending Cadet"),
        ("rejected_by_cadet", "Rejected by Cadet"),
        ("pending_officer", "Pending Officer"),
        ("rejected_by_officer", "Rejected by Officer"),
        ("approved", "Approved"),
        ("invalid", "Invalid"),
    )

    complainants = models.ManyToManyField(
        to="user.User",
        related_name="complaints",
    )

    description = models.TextField()

    cadet = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="cadet_complaints",
    )

    cadet_rejection_reason = models.TextField(default="Null")

    police_officer = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="officer_complaints",
    )

    rejection_count = models.IntegerField(
        default=0,
    )

    case = models.ForeignKey(
        to="Case",
        on_delete=models.PROTECT,
        related_name="complaints",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20, choices=COMPLAINT_STATUS, default="pending_cadet"
    )

    officer_rejection_reason = models.TextField(blank=True, null=True)
