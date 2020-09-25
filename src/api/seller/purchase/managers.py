from datetime import timedelta

from django.db import models
from django.db.models import Count, Case, When, BooleanField, IntegerField, Sum
from django.utils import timezone


class PurchaseQueryset(models.QuerySet):

    def for_eater(self, eater):
        return self.filter(eater=eater)

    def select_related_rating(self):
        return self.select_related('rating')

    def select_related_eater(self):
        return self.select_related('eater')

    def customer_type(self):
        eater_count = self.annotate(
            eater_count=Count('eater__purchases')
        )
        return eater_count.annotate(
            customer=Case(
                When(eater_count=1, then=True),
                default=False,
                output_field=BooleanField()
            )
        )

    def discount(self):
        eater_discount = self.annotate(
            eater_discount=Sum(Case(When(items__is_discounted=True, then=1),
                                    default=0,
                                    output_field=IntegerField())
                               ))
        return eater_discount.annotate(discount=Case(
            When(eater_discount=0, then=False),
            default=True,
            output_field=BooleanField()))

    def with_rating(self, rating):
        return self.filter(rating__overall_rating=rating)

    def with_dishes(self, dish):
        return self.filter(items__dishes__id=dish)

    def with_days(self, days):
        requried_date = timezone.now() - timedelta(days=int(days))
        return self.filter(created_at__date__gte=requried_date)
