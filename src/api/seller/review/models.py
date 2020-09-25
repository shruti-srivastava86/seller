from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from seller.models import TimestampedModel
from seller.review.managers import RatingQueryset


class Rating(TimestampedModel):
    objects = RatingQueryset.as_manager()

    purchase = models.OneToOneField(
        'purchase.Purchase',
        related_name='rating'
    )
    overall_rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    text = models.TextField(
        blank=True
    )

    def __str__(self):
        return "{}: eater - {}".format(self.id, self.purchase.eater.email)

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Rating"
        indexes = [
            models.Index(fields=['overall_rating']),
            models.Index(fields=['purchase']),
        ]
