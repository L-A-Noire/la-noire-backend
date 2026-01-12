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
