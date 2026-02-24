from django.db import models

from crime.models import Crime, Case


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

    is_confirmed = models.BooleanField(default=False)

    seen_at = models.DateTimeField()

    witnesses = models.ManyToManyField(
        to="user.User",
        related_name="witnessed_scenes",
    )

    location = models.CharField(max_length=500, null=True)
    description = models.TextField(null=True)

    def create_case(self, crime_level):
        crime = Crime.objects.create(
            crime_level
        )
        Case.objects.create(
            crime=crime,
            is_from_crime_scene=True,
        )
