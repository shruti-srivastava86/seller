from datetime import timedelta

from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Q, F, DateTimeField, DateField, TimeField
from django.db.models.functions import Cast
from django.utils import timezone

from seller.user import enums


class HawkkerUserManager(UserManager):
    """
        Custom manager for the User model.
    """

    def _create_user(self, **kwargs):
        user = self.model(**kwargs)
        user.save(using=self._db)
        user.is_active = True
        user.set_password(kwargs.get('password'))
        user.save(using=self._db)
        return user

    def create_user(self, **kwargs):
        return self._create_user(**kwargs)

    def create_superuser(self, **kwargs):
        kwargs.setdefault('user_type', enums.ADMIN)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)
        return self._create_user(**kwargs)

    def create_guest_user(self, **kwargs):
        return self._create_user(**kwargs)


class HawkkerQueryset(models.QuerySet):

    def with_id(self, id):
        return self.filter(id=id)

    def with_email(self, email):
        return self.filter(email=email)

    def contains_email(self, email):
        return self.filter(email__icontains=email)

    def contains_name(self, name):
        return self.filter(name__icontains=name)

    def active(self):
        return self.filter(is_active=True)

    def is_vendor(self):
        return self.filter(Q(user_type=enums.VENDOR) | Q(is_superuser=True))

    def is_eater(self):
        return self.filter(user_type=enums.EATER)

    def with_user_local_date_time(self):
        """
            To add user local date time in query
        """
        return self.annotate(
            local_time=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')) + timedelta(minutes=14.5),
                DateTimeField()
            ),
            check_out_time_before=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')) + timedelta(minutes=14.5),
                TimeField()
            ),
            check_out_time_after=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')) + timedelta(minutes=16.5),
                TimeField()
            ),
            auto_check_out_time_before=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')) - timedelta(minutes=1),
                TimeField()
            ),
            auto_check_out_time_after=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')),
                TimeField()
            ),
            check_in_time_before=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')) - timedelta(minutes=15.5),
                TimeField()
            ),
            check_in_time_after=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')) - timedelta(minutes=13.5),
                TimeField()
            ),
            local_date=Cast(
                timezone.now() + (timedelta(seconds=1) * F('time_offset')),
                DateField(

                )
            ),


        )


class GeneralSettingsQueryset(models.QuerySet):

    def get_settings(self):
        return self.order_by('-created_at').first()

    def get_convert_to_pounds(self, coins):
        return self.get_settings().one_coin_to_pounds * coins


class TransactionQueryset(models.QuerySet):

    def success_transactions(self):
        return self.filter(status=enums.SUCCESS)

    def with_valid_qr_id(self, qr_id):
        return self.filter(qr_id=qr_id, status=enums.PENDING)
