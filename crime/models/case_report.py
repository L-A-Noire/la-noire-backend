from django.db import models


class CaseReport(models.Model):
    reporter = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="case_reports",
    )

    case = models.OneToOneField(
        to="Case",
        on_delete=models.PROTECT,
        related_name="case_report",
    )

    # optional
    reported_at = models.DateTimeField(auto_now_add=True)
    REPORT_STATUS = (
        ("pending"),
        ("approved"),
        ("rejected"),
    )
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS)
    # for rejection:
    rejection_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        to="user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports",
    )
