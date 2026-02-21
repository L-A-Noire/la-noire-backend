from django.db import models

from crime.models import Case


class Interrogation(models.Model):
    suspect_crime = models.ForeignKey(
        to="SuspectCrime", on_delete=models.PROTECT, related_name="interrogations"
    )

    case = models.ForeignKey(
        to=Case, on_delete=models.PROTECT, related_name="interrogations"
    )

    interrogators = models.ManyToManyField(
        to="user.User",
        related_name="conducted_interrogations",
        help_text="Detective and Sergeant conducting the interrogation",
    )

    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=500)
    notes = models.TextField()

    detective_score = models.IntegerField(null=True, blank=True)
    sergeant_score = models.IntegerField(null=True, blank=True)
    final_score = models.IntegerField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        to="user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_interrogations",
    )

    review_notes = models.TextField(blank=True, null=True)
