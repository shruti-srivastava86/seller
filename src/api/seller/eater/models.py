from django.db import models

from seller.user.models import User
from seller.eater.managers import EaterUserManager
from seller.eater import enums


class Eater(User):
    """
        Model representing a Eater.
    """
    objects = EaterUserManager()

    dietary_preference = models.ManyToManyField(
        'dish.Dietary',
        related_name='eaters',
        blank=True
    )
    favourite_vendors = models.ManyToManyField(
        'vendor.Vendor',
        related_name='favourite_by',
        blank=True
    )

    notification_preference = models.OneToOneField(
        'notification.EaterPreference',
        null=True,
        blank=True
    )
    status = models.PositiveSmallIntegerField(
        choices=enums.EATER_STATUS,
        default=enums.ACTIVE
    )
    home_market = models.ForeignKey(
        'vendor.Market',
        null=True,
        blank=True
    )
    type = models.IntegerField(choices=enums.TYPE_CHOICE, default=enums.EMAIL_SIGNUP)

    facebook_id = models.CharField(max_length=255,
                                   db_index=True,
                                   blank=True,
                                   null=True,
                                   unique=True)
    is_dietary_preference = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Eater"
        verbose_name_plural = "Eater"

    @property
    def reviews(self):
        from seller.review.models import Rating
        return Rating.objects.filter(purchase__eater=self)
