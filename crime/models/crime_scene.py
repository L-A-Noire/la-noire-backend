from django.db import models

from crime.models import Case, Crime
from witness.models import Testimony


class CrimeScene(models.Model):
    crime = models.OneToOneField(
        to="Crime",
        on_delete=models.PROTECT,
        related_name="crime_scenes",
        null=True,
        blank=True,
    )

    examiner = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="examined_scenes",
        null=True,
        blank=True,
    )

    testimony = models.OneToOneField(
        to=Testimony,
        on_delete=models.DO_NOTHING,
        related_name="crime_scene",
        null=True,
        blank=True,
    )

    is_confirmed = models.BooleanField(default=False)

    seen_at = models.DateTimeField()

    witness = models.ForeignKey(
        to="user.User",
        on_delete=models.PROTECT,
        related_name="witnessed_scenes",
        null=True,
        blank=True,
    )

    location = models.CharField(max_length=500, null=True)
    description = models.TextField(null=True)

    def create_case(self, crime_level):
        crime = Crime.objects.create(level=crime_level)
        case = Case.objects.create(
            crime=crime,
            is_from_crime_scene=True,
        )

        if self.testimony:
            self.testimony.case = case
            self.testimony.save()
        self.crime = crime
        self.save()
