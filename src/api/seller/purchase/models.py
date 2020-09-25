from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from rest_framework.utils.encoders import JSONEncoder

from seller.models import TimestampedModel
from seller.purchase.managers import PurchaseQueryset
from django.contrib.gis.db import models as postgis


class PurchaseItem(TimestampedModel):
    purchase = models.ForeignKey(
        'Purchase',
        related_name='items'
    )
    dishes = models.ForeignKey(
        'dish.Dish',
        related_name='items'
    )
    quantity = models.IntegerField()
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    special = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)
    current_price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    total_price_paid = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):
        return "{} - {} - {}".format(self.purchase, self.dishes, self.quantity)


class Purchase(TimestampedModel):
    objects = PurchaseQueryset.as_manager()

    details = JSONField(
        null=True,
        help_text="Editable only in DEBUG mode.",
        encoder=JSONEncoder
    )
    eater = models.ForeignKey(
        'eater.Eater',
        related_name='purchases'
    )
    vendor = models.ForeignKey(
        'vendor.Vendor',
        related_name='purchases'
    )
    waiting_time = models.IntegerField()
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    location = postgis.PointField(
        null=True,
        blank=True
    )
    vendor_location = postgis.PointField(
        null=True,
        blank=True
    )
    dish_not_listed = models.BooleanField(default=False)
    not_listed_dish = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    check_in = models.BooleanField(default=False)
    eater_type = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.eater.email, self.vendor.email)

    class Meta:
        verbose_name = "Purchase"
        verbose_name_plural = "Purchase"
        indexes = [
            models.Index(fields=['eater']),
            models.Index(fields=['vendor']),
            GinIndex(fields=['details'])
        ]

    @property
    def price_paid(self):
        """Returns the price paid for the transaction

        This takes account for any temporary prices that may
        have come into play
        """
        if not self.details:
            return 0
        return sum([
            d['total_price_paid'] for d in self.details
            if 'total_price_paid' in d])

    @property
    def full_price_amount(self):
        """Returns the price paid for the transaction

        This takes account for any temporary prices that may
        have come into play
        """
        if not self.details:
            return 0
        return sum([
            d['full_price'] * d['quantity'] for d in self.details
            if 'full_price' in d])

    @property
    def has_special(self):
        """Returns if this purchase included a special or not
        """
        if not self.details:
            return False
        return any([d['special'] for d in self.details if 'special' in d])
