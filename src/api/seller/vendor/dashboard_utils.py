from django.db.models import F, Avg, Sum
from django.db.models.functions import Coalesce


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


def vendor_profile_views(vendor, date):
    return vendor.profile_views.filter(
        created_at__lt=date
    ).annotate(
        views=(F('count'))
    ).aggregate(
        total_views=Coalesce(Sum('views'), 0)
    )


def vendor_profile_views_30(vendor, date):
    return vendor.profile_views.filter(
        created_at__gt=date
    ).annotate(
        views=(F('count'))
    ).aggregate(
        total_views=Coalesce(Sum('views'), 0)
    )
