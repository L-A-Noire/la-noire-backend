from django.db import models
from django.db.models import Q

from witness.models.evidence import Evidence


class VehicleEvidence(Evidence):
    vehicle_model = models.CharField(
        max_length=50,
    )

    registration_plate_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    color = models.CharField(
        max_length=50,
    )

    serial_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="exactly_one_of_serial_or_plate",
                condition=(
                    (
                        Q(serial_number__isnull=False)
                        & Q(registration_plate_number__isnull=True)
                    )
                    | (
                        Q(serial_number__isnull=True)
                        & Q(registration_plate_number__isnull=False)
                    )
                ),
            ),
        ]
