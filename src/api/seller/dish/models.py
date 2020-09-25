from decimal import Decimal

from django.db import models

from seller.dish.managers import DishQueryset
from seller.models import NameAbstractModel


class Dietary(NameAbstractModel):

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Dietary"
        verbose_name_plural = "Dietary"
        indexes = [
            models.Index(fields=['name']),
        ]


class Cuisine(NameAbstractModel):

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Cuisine"
        verbose_name_plural = "Cuisine"
        indexes = [
            models.Index(fields=['name']),
        ]


class Allergens(NameAbstractModel):

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Allergen"
        verbose_name_plural = "Allergen"
        indexes = [
            models.Index(fields=['name']),
        ]


class Dish(NameAbstractModel):
    objects = DishQueryset.as_manager()

    business = models.ForeignKey(
        'vendor.Business',
        related_name="dishes"
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    temporary_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    active = models.BooleanField(
        default=True
    )
    special = models.BooleanField(
        default=False
    )
    deleted = models.BooleanField(
        default=False
    )
    dietary_information = models.ManyToManyField(
        'dish.Dietary',
        related_name='dishes',
        blank=True
    )
    serial_id = models.IntegerField(default=0)

    def __str__(self):
        return "{}: {}".format(self.id, self.name)

    class Meta:
        verbose_name = "Dish"
        verbose_name_plural = "Dish"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['temporary_price']),
            models.Index(fields=['active']),
            models.Index(fields=['special']),
        ]

    @property
    def current_price(self):
        """Returns the correct current price of an item
        taking into account any discounts
        """
        if self.has_temporary_price:
            return self.temporary_price
        return self.price

    @property
    def has_temporary_price(self):
        """Returns true if this dish has a temporary price"""
        return self.temporary_price > Decimal('0.00')
