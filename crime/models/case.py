from django.db import models


class Case(models.Model):
    crime = models.OneToOneField(
        to='Crime',
        on_delete=models.PROTECT,
        related_name='case',
        null=True,
        blank=True,
    )

    # optional
    CASE_STATUS = (
        ('open'),
        ('pending'),
        ('investigating'),
        ('solved'),
        ('closed'),
        ('archived'),
        ('dismissed'),
    )
    title = models.CharField(max_length=200)
    case_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=CASE_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    is_from_crime_scene = models.BooleanField(default=False)
    # can also mention assignee:
    # detective = models.ForeignKey(
    #     to="user.User",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="detective_cases",
    #     limit_choices_to={'role__title': 'Detective'},
    # )
