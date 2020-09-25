from datetime import timedelta

from django.contrib.auth.models import UserManager
from django.contrib.gis.db.models.functions import Distance
from django.db import models
from django.db.models import Q, F, TimeField, DateField
from django.db.models.functions import Cast
from django.utils import timezone

from seller.user import enums
from seller.vendor import enums as vendor_enums


class VendorUserManager(UserManager):

    def create_user(self, **kwargs):
        user = self.model(**kwargs)
        user.save(using=self._db)
        user.is_active = True
        user.user_type = enums.VENDOR
        user.set_password(kwargs.get('password'))
        user.location = kwargs.get('location')
        user.save(using=self._db)
        return user


class VendorQueryset(models.QuerySet):

    def closed(self):
        return self.filter(
            business__open=False
        )

    def open(self):
        return self.filter(
            business__open=True
        )

    def with_email(self, email):
        return self.filter(
            email=email
        )

    def contains_email(self, email):
        return self.filter(
            email__icontains=email
        )

    def contains_name(self, name):
        return self.filter(
            name__icontains=name
        )

    def active(self):
        return self.filter(
            is_active=True
        )

    def approved(self):
        return self.filter(
            status=vendor_enums.APPROVED
        )

    def annotate_distance(self, point):
        return self.annotate(
            distance=Distance('location', point)
        )

    def distance_lte(self, distance):
        return self.filter(
            distance__lte=distance
        )

    def favourite_for(self, eater):
        return self.filter(
            favourite_by=eater
        )

    def not_favourite_for(self, eater):
        return self.filter(
            ~Q(favourite_by=eater)
        )

    def without_business(self):
        return self.filter(
            business__isnull=True
        )

    def with_business(self):
        return self.filter(
            business__isnull=False
        )

    def with_active_dishes(self):
        return self.filter(
            business__dishes__active=True
        ).distinct()

    def with_cash(self):
        return self.filter(
            business__cash=True
        )

    def with_card(self):
        return self.filter(
            business__card=True
        )

    def with_cash_card(self):
        return self.filter(
            Q(business__card=True) | Q(business__cash=True)
        )

    def without_cash(self):
        return self.filter(
            business__cash=False
        )

    def without_card(self):
        return self.filter(
            business__card=False
        )

    def with_offer(self):
        return self.filter(
            business__offer_active=True
        )

    def with_discount(self):
        return self.filter(
            business__discount_active=True
        )

    def without_discount(self):
        return self.filter(
            business__discount_active=False
        )

    def without_offer(self):
        return self.filter(
            business__offer_active=False
        )

    def with_cuisines(self, cuisines):
        return self.filter(
            business__cuisine__id__in=cuisines
        )

    def with_dietary(self, dietary):
        return self.filter(
            business__dishes__dietary_information__id__in=dietary,
            business__dishes__active=True
        )

    def with_rating(self, ratings):
        for i, rating in enumerate(ratings):
            if i == 0:
                queryset = self.filter(
                    average_rating__range=[
                        float(rating),
                        int(float(rating) + 0.99)
                    ]
                )
            else:
                queryset = queryset | self.filter(
                    average_rating__range=[
                        float(rating),
                        float(int(rating) + 0.99)
                    ]
                )
        return queryset

    def select_related_business(self):
        return self.select_related(
            'business',
        )

    def prefetch_related_dishes(self):
        return self.prefetch_related(
            'business__dishes'
        )

    def prefetch_related_dietary(self):
        return self.prefetch_related(
            'business__dishes__dietary_information'
        )

    def prefetch_related_cuisine(self):
        return self.prefetch_related(
            'business__cuisine'
        )


class BusinessQueryset(models.QuerySet):

    def previous_day_open(self):
        return self.filter(
            open=True
        )

    def with_user_local_date_time(self):
        """
            To add user local date time in query
        """
        return self.annotate(
            auto_check_out_time_before=Cast(
                timezone.now() + (timedelta(seconds=1) * F('vendor__time_offset')) - timedelta(minutes=1),
                TimeField()
            ),
            auto_check_out_time_after=Cast(
                timezone.now() + (timedelta(seconds=1) * F('vendor__time_offset')),
                TimeField()
            ),

            local_date=Cast(
                timezone.now() + (timedelta(seconds=1) * F('vendor__time_offset')),
                DateField(

                )
            ),

        )


class OpeningHoursQueryset(models.QuerySet):

    def opening_hours_for_day(self, day):
        return self.filter(
            weekday=day
        )


class ImageQuerySet(models.QuerySet):

    def hero_photo(self):
        return self.filter(hero=True)
