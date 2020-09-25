from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from seller.models import TimestampedModel
from seller.notification.managers import NotificationQuerySet
from seller.notification.constants import NOTIFICATIONS
from seller.notification import enums


class VendorPreference(TimestampedModel):
    checkin_checkout = models.BooleanField(
        default=True
    )
    marketing = models.BooleanField(
        default=True
    )
    support = models.BooleanField(
        default=True
    )

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        verbose_name = "Vendor Preference"
        verbose_name_plural = "Vendor Preference"
        indexes = [
            models.Index(fields=['checkin_checkout']),
            models.Index(fields=['marketing']),
            models.Index(fields=['support']),
        ]


class EaterPreference(TimestampedModel):
    marketing = models.BooleanField(
        default=True
    )
    review = models.BooleanField(
        default=True
    )

    def __str__(self):
        return "{}".format(self.id)

    class Meta:
        verbose_name = "Eater Preference"
        verbose_name_plural = "Eater Preference"
        indexes = [
            models.Index(fields=['marketing']),
            models.Index(fields=['review']),
        ]


class Notifications(TimestampedModel):
    """
        Model representing a Notification sent to a user.
    """
    objects = NotificationQuerySet.as_manager()

    user = models.ForeignKey(
        'user.User',
        related_name='notifications'
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
    context = models.TextField(
        max_length=255
    )
    message = models.TextField(
        max_length=255
    )
    read = models.BooleanField(
        default=False
    )

    icon = models.ImageField(
        null=True, blank=True,
        help_text='Small icon sized image displayed next to a notification')
    image = models.ImageField(
        null=True, blank=True,
        help_text='Larger image used when expanding notifications')

    notification_type = models.IntegerField(default=NOTIFICATIONS)

    def __str__(self):
        return "{} - {}".format(self.id, self.user.email)

    class Meta:
        verbose_name = 'Notifications'
        verbose_name_plural = 'Notifications'


class EmailTemplate(TimestampedModel):
    type = models.IntegerField(choices=enums.EMAIL_TYPE)
    content = models.TextField()

    def __str__(self):
        return "{} - {}".format(self.type, self.content)
