import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django_pgviews import view as pg
from seller.models import TimestampedModel, NameAbstractModel
from seller.user import enums
from seller.user.managers import (
    HawkkerUserManager,
    HawkkerQueryset,
    GeneralSettingsQueryset,
    TransactionQueryset
)


class User(NameAbstractModel, AbstractBaseUser, PermissionsMixin):
    """
        Model representing a User.
    """
    objects = HawkkerUserManager()

    filter = HawkkerQueryset.as_manager()

    user_type = models.PositiveSmallIntegerField(
        choices=enums.USER_TYPES,
        default=enums.EATER
    )
    email = models.EmailField(
        unique=True
    )
    coins = models.PositiveIntegerField(
        _('reward coins'),
        default=0
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('log into django admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True
    )
    location = models.PointField(
        null=True,
        blank=True
    )
    devices = models.ManyToManyField(
        'scarface.Device',
        blank=True
    )
    time_offset = models.IntegerField(
        default=0
    )
    notes = models.TextField(
        blank=True, null=True, help_text='''
        Hawkker Team Notes.
        These are for staff use only and are not displayed to
        any other users''')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __unicode__(self):
        return self.email

    def get_short_name(self):
        return self.name.split(" ")[0]

    def get_full_name(self):
        return self.name

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "User"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['location']),
        ]
        permissions = (
            ('sql_explorer', 'Can Access SQL Explorer'),
        )


class Transaction(TimestampedModel):
    objects = TransactionQueryset.as_manager()

    user = models.ForeignKey(
        'user.User',
        related_name='transactions'
    )
    qr_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    purchase = models.ForeignKey(
        'purchase.Purchase',
        related_name='transactions',
        blank=True,
        null=True
    )
    coins = models.PositiveIntegerField(
        _('reward coins'),
        default=0
    )
    amount = models.DecimalField(
        blank=False,
        null=True,
        decimal_places=2,
        max_digits=8
    )

    # Balance is a running balance of the number of coins.
    # Think of it like the "current balance" field on
    # a bank statement
    balance = models.PositiveIntegerField(
        _("Balance coins"),
        default=0
    )
    type = models.PositiveSmallIntegerField(
        choices=enums.TRANSACTION_TYPES,
    )
    reason = models.PositiveSmallIntegerField(
        choices=enums.TRANSACTION_REASONS,
    )
    status = models.PositiveSmallIntegerField(
        choices=enums.TRANSACTION_STATUS,
        default=enums.SUCCESS
    )
    note = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transaction"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['type']),
            models.Index(fields=['reason']),
            models.Index(fields=['status']),
            models.Index(fields=['type', 'reason', 'status']),
        ]


class TransactionLogView(pg.View):
    """A Postgres View which joins together transactions based
    on their QR ID.

    This allows the admin panel to view transactions in the client's
    requested manor
    """
    sql = """
SELECT
    DISTINCT ON (ut.qr_id)
    ut.id,
    ut.qr_id,
    ut.created_at AS created_at,
    debit_tr.id AS debit_id,
    debit_tr.coins AS debit_amount,
    debit_tr.reason AS debit_reason,
    debit_tr.user_id AS debit_user_id,
    credit_tr.id AS credit_id,
    credit_tr.coins AS credit_amount,
    credit_tr.reason AS credit_reason,
    credit_tr.user_id AS credit_user_id
FROM user_transaction ut
LEFT OUTER JOIN (
    SELECT * FROM user_transaction WHERE qr_id = qr_id AND "type" = 0
) debit_tr ON debit_tr.qr_id = ut.qr_id
LEFT OUTER JOIN (
    SELECT * FROM user_transaction WHERE qr_id = qr_id AND "type" = 1
) credit_tr ON credit_tr.qr_id = ut.qr_id
"""
    qr_id = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    debit = models.ForeignKey(
        Transaction, on_delete=models.DO_NOTHING, related_name='logview_debits')
    debit_amount = models.IntegerField()
    debit_reason = models.PositiveSmallIntegerField(
        choices=enums.TRANSACTION_REASONS,
    )
    debit_user = models.ForeignKey(
        User, null=True, on_delete=models.DO_NOTHING, related_name='transactionlogview_debits')

    credit = models.ForeignKey(
        Transaction, on_delete=models.DO_NOTHING, related_name='logview_credits')
    credit_amount = models.IntegerField()
    credit_reason = models.PositiveSmallIntegerField(
        choices=enums.TRANSACTION_REASONS,
    )
    credit_user = models.ForeignKey(
        User, null=True, on_delete=models.DO_NOTHING, related_name='transactionlogview_credits')


class ForgotPassword(TimestampedModel):
    user = models.ForeignKey(
        'user.User',
        related_name='forgotten_passwords'
    )
    token = models.CharField(
        max_length=255
    )

    def __str__(self):
        return "{} - {}".format(self.id, self.user.email)

    class Meta:
        verbose_name = _('Forgot Password')
        verbose_name_plural = _('Forgot Password')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
        ]


class GeneralSettings(TimestampedModel):
    objects = GeneralSettingsQueryset.as_manager()

    search_radius_in_miles = models.IntegerField(
        default=settings.DEFAULT_SEARCH_RANGE_IN_MILES
    )
    incomplete_profile_email_reminder_days = models.SmallIntegerField(
        default=7
    )
    one_coin_to_pounds = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    minimum_coins_redeemable = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    maximum_coins_redeemable = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    coins_incremental_value = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    scan_qr_points = models.IntegerField()
    review_points = models.IntegerField()
    eater_review_reminder = models.IntegerField()
    vendor_checkin_reminder_before_time = models.IntegerField()
    vendor_checkin_reminder_after_time = models.IntegerField()
    dietary_preference = models.IntegerField()
    minimum_reviews_vendor = models.IntegerField()

    class Meta:
        verbose_name = _('General Settings')
        verbose_name_plural = _('General Settings')


class ReportVendorList(NameAbstractModel):
    class Meta:
        verbose_name = "Report Vendor Reason"
        verbose_name_plural = "Report Vendor Reason"

    def __str__(self):
        return "{}".format(self.name)


class ReportVendor(TimestampedModel):
    class Meta:
        verbose_name = "Vendor Report"
        verbose_name_plural = "Vendor Report"

    eater = models.ForeignKey('eater.Eater')
    vendor = models.ForeignKey('vendor.Vendor')
    report = models.ForeignKey(ReportVendorList)
    message = models.TextField(blank=True)
    processed = models.BooleanField(
        default=False,
        help_text='''
        Use this checkbox to mark this report as processed to keep
        track of what reports need actioning''')

    def __str__(self):
        return "{} - {} - {}".format(self.eater, self.vendor, self.report)


class SupportEater(TimestampedModel):
    eater = models.ForeignKey('eater.Eater', related_name="support_eater")
    message = models.TextField()

    def __str__(self):
        return "{} - {}".format(self.eater, self.message)


class SearchTerms(TimestampedModel):
    user = models.ForeignKey(
        'user.User',
        related_name='search'

    )
    word = models.CharField(
        max_length=255
    )

    def __str__(self):
        return "{}-{}".format(self.user, self.word)
