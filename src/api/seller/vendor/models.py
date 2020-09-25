import uuid

from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.translation import ugettext_lazy as _

from seller.models import TimestampedModel, NameAbstractModel
from seller.user.models import User
from seller.user.utils import business_photo
from seller.vendor import enums
from seller.vendor.managers import (
    VendorUserManager,
    VendorQueryset,
    OpeningHoursQueryset,
    BusinessQueryset,
    ImageQuerySet
)


class Vendor(User):
    """
        Model representing a Vendor.
    """
    objects = VendorUserManager()
    filter = VendorQueryset.as_manager()

    address = models.TextField(
        blank=True
    )
    status = models.PositiveSmallIntegerField(
        choices=enums.VENDOR_STATUS,
        default=enums.INCOMPLETE,
        help_text=(
            '<div><br/>Status defines vendor account status. The following are the options:<br/>'
            '1. incomplete - Vendor signed up using email and password<br/>'
            '2. Inprogress - Vendor verified his email address<br/>'
            '3. Completed - Vendor completed and submitted his business profile<br/>'
            '4. Approved - Hawkker approved the vendor<br/>'
            '5. Rejected - Hawkker rejected the vendor'
            '6. Suspened - Hawkker suspened the vendor'
            '</div>'
        )
    )
    onboarding_stage = models.PositiveSmallIntegerField(
        choices=enums.ONBOARDING_STAGE,
        default=enums.STAGE1
    )
    notification_preference = models.OneToOneField(
        'notification.VendorPreference',
        null=True,
        blank=True
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    address_line_1 = models.TextField(
        blank=True
    )
    address_line_2 = models.TextField(
        blank=True
    )
    city = models.CharField(
        max_length=255,
        blank=True
    )
    county = models.CharField(
        max_length=255,
        blank=True
    )
    postcode = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendor"
        indexes = [
            models.Index(fields=['notification_preference']),
            models.Index(fields=['status']),
        ]

    @property
    def reviews(self):
        from seller.review.models import Rating
        return Rating.objects.filter(purchase__vendor=self)


class Business(NameAbstractModel):
    objects = BusinessQueryset.as_manager()
    name = models.CharField(
        max_length=255,
        unique=True
    )
    vendor = models.OneToOneField(
        'vendor.Vendor',
        related_name='business'
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    biography = models.TextField(
        blank=True
    )
    tagline = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    photos = models.ManyToManyField(
        'vendor.Image',
        related_name='business'
    )
    cash = models.BooleanField(
        default=False
    )
    card = models.BooleanField(
        default=False
    )
    social_links = JSONField(
        null=True
    )
    ingredients = ArrayField(
        models.CharField(
            max_length=255
        ),
        null=True,
        blank=True
    )
    allergens = models.ManyToManyField(
        'dish.Allergens',
        related_name='business'
    )
    cuisine = models.ManyToManyField(
        'dish.Cuisine',
        related_name='business'
    )
    open = models.BooleanField(
        default=False
    )
    check_out = models.TimeField(
        null=True,
        blank=True
    )
    offer_active = models.BooleanField(
        default=False
    )
    offer = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    discount_active = models.BooleanField(
        default=False
    )
    home_market = models.ManyToManyField(
        'vendor.Market',
        related_name='market'
    )

    def __str__(self):
        return "{}: {} ({})".format(self.id, self.name, self.vendor.name)

    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Business"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['cash']),
            models.Index(fields=['card']),
            models.Index(fields=['ingredients']),
            models.Index(fields=['open']),
            GinIndex(fields=['social_links']),
        ]

    @property
    def dishes_with_related(self):
        return self.dishes.prefetch_related('dietary_information')


class Market(NameAbstractModel):
    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Market"
        indexes = [
            models.Index(fields=['name']),
        ]


class Image(TimestampedModel):
    objects = ImageQuerySet.as_manager()

    image = models.ImageField(
        upload_to=business_photo,
        max_length=1024
    )
    hero = models.BooleanField(
        default=False
    )

    def __str__(self):
        return "Image -> {} : {}".format(self.id, self.image)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Image"
        indexes = [
            models.Index(fields=['image']),
            models.Index(fields=['hero'])
        ]


class OpeningHours(TimestampedModel):
    """
        Business opening times defined each day using one or more start and end times.
    """
    objects = OpeningHoursQueryset()

    business = models.ForeignKey(
        'vendor.Business',
        related_name="opening_hours"
    )
    weekday = models.IntegerField(
        _('Weekday'),
        choices=enums.WEEKDAYS
    )
    from_hour = models.TimeField(
        _('Opening'),
        blank=True,
        null=True
    )
    to_hour = models.TimeField(
        _('Closing'),
        blank=True,
        null=True
    )
    open = models.BooleanField(
        default=True
    )

    def __str__(self):
        return "{} - {} ({} - {}) - {}".format(
            self.business.name,
            self.get_weekday_display(),
            self.from_hour,
            self.to_hour,
            self.open
        )

    class Meta:
        verbose_name = _('Opening Hours')
        verbose_name_plural = _('Opening Hours')
        indexes = [
            models.Index(fields=['weekday']),
            models.Index(fields=['from_hour', 'to_hour']),
        ]
        ordering = ['weekday', ]


class BusinessCheckinCheckout(TimestampedModel):
    business = models.ForeignKey(
        'vendor.Business',
        related_name='checkin'
    )
    check_in = models.TimeField(
    )
    check_out = models.TimeField(
    )

    def __str__(self):
        return "{} - {} - {}".format(
            self.business,
            self.check_in,
            self.check_out
        )


class VendorProfileViews(TimestampedModel):
    vendor = models.ForeignKey(
        'vendor.Vendor',
        related_name='profile_views'
    )
    count = models.PositiveIntegerField(default=0)
    guest_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} - {} - {} - {}".format(
            self.created_at.date(),
            self.vendor,
            self.count,
            self.guest_count
        )
