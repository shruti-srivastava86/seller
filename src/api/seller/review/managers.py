from django.db import models
from django.db.models import F, FloatField, OuterRef, Count, Avg
from django.db.models.functions import Cast, Coalesce


class RatingQueryset(models.QuerySet):

    def with_average_rating(self):
        return self.annotate(
            average_rating=Cast(
                (
                        F('overall_rating')
                ) / 4.0, FloatField()
            )
        )

    def for_vendor(self, vendor):
        return self.filter(
            purchase__vendor=vendor
        )

    def for_eater(self, eater):
        return self.filter(
            purchase__eater=eater
        )

    def select_related_eater(self):
        return self.prefetch_related('purchase__eater')

    def select_related_vendor(self):
        return self.prefetch_related('purchase__vendor')

    def total_rating_subquery(self):
        return self.filter(
            purchase__vendor__id=OuterRef('id')
        ).annotate(
            ratings_count=Count(F('id'))
        ).values(
            'ratings_count'
        ).annotate(
            total_ratings=Coalesce(F('ratings_count'), 0)
        ).values(
            'total_ratings'
        )[:1]

    def average_rating_subquery(self):
        return self.filter(
            purchase__vendor__id=OuterRef('id')
        ).annotate(
            total_average_rating=Cast(
                Avg(
                    (
                            F('overall_rating')
                    )
                ),
                FloatField()
            )
        ).values(
            'total_average_rating'
        ).annotate(
            average_rating=Coalesce(F('total_average_rating'), 0)
        ).values(
            'average_rating'
        )[:1]
