from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NameAbstractModel(TimestampedModel):
    name = models.CharField(
        max_length=255
    )

    class Meta:
        abstract = True
