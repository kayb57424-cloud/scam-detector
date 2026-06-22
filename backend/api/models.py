from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    reporter_region = models.CharField(
        max_length=100,
        default="Unknown"
    )

    source_type = models.CharField(
        max_length=50,
        default="SMS"
    )

    phone_number = models.CharField(
        max_length=255
    )

    # NEW FIELD
    phone_country = models.CharField(
        max_length=100,
        default="Unknown"
    )

    message = models.TextField()

    result = models.CharField(
        max_length=20
    )

    region = models.CharField(
        max_length=100,
        default="Unknown"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.phone_number