from django.db import models


class Complaint(models.Model):
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

    is_confirmed_by_cadet = models.BooleanField()

    rejection_reason = models.TextField()

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

    # optional
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    COMPLAINT_STATUS = (
        ("pending_cadet"),
        ("rejected_by_cadet"),
        ("pending_officer"),
        ("rejected_by_officer"),
        ("approved"),
        ("case_created"),
        ("invalid"),
    )
    status = models.CharField(
        max_length=20, choices=COMPLAINT_STATUS, default="pending_cadet")

    is_confirmed_by_officer = models.BooleanField(null=True, blank=True)
    officer_rejection_reason = models.TextField(blank=True, null=True)
