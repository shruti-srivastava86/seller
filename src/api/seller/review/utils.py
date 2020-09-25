from django.db.models import F, Avg, Count
from django.db.models.functions import Coalesce


def vendor_total_average_ratings(vendor):
    return vendor.purchases.annotate(
        total_average_rating=(F('rating__overall_rating'))
    ).aggregate(
        overall_rating_average=Coalesce(Avg('rating__overall_rating'), 0),
        average_rating=Coalesce(Avg('total_average_rating'), 0),
        total_ratings=Count('rating')
    )


def vendor_total_average_wait_time(vendor, date):
    return vendor.purchases.filter(created_at__lt=date).annotate(
        total_average_wait_time=(F('waiting_time'))
    ).aggregate(
        overall_wait_time=Coalesce(Avg('waiting_time'), 0),
        average_wait_time=Coalesce(Avg('total_average_wait_time'), 0)
    )


def vendor_total_average_wait_time_30(vendor, date):
    return vendor.purchases.filter(created_at__gt=date).annotate(
        total_average_wait_time=(F('waiting_time'))
    ).aggregate(
        overall_wait_time=Coalesce(Avg('waiting_time'), 0),
        average_wait_time=Coalesce(Avg('total_average_wait_time'), 0)
    )
