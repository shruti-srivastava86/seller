from datetime import timedelta

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from seller.dish.models import Dish
from seller.notification.constants import CHECKIN_CHECKOUT
from seller.notification.utils import send_message_to_devices
from seller.user import enums
from seller.user.models import GeneralSettings, User
from seller.vendor.models import Business, Vendor
from seller.vendor.utils import send_profile_complete_reminder_email, unread_count


@periodic_task(run_every=(crontab(minute=0, hour=0)), name="vendor_auto_checkout")
def task_vendor_auto_checkout():
    """
        Task to auto checkout vendors who have not checked out the previous day
        Runs daily midnight
    """
    try:
        Business.objects.previous_day_open().update(
            open=False,
            check_out=None,
            offer_active=False,
            discount_active=False
        )
        print("Complete auto checkout task")
    except Exception as e:
        print("Failed to auto checkout with error: {}".format(str(e)))


@periodic_task(run_every=(crontab(minute=0, hour=0)), name="vendor_profile_pending")
def task_vendor_profile_pending_reminder_email():
    """
        Task to send out email reminder to vendors who have not completed their profile
        Runs daily midnight
    """
    try:
        general_settings = GeneralSettings.objects.get_settings()
        if general_settings:
            days = general_settings.incomplete_profile_email_reminder_days - 1
        else:
            days = 6
        send_profile_complete_reminder_email(
            Vendor.filter.without_business().filter(
                created_at=timezone.now() - timedelta(days=days)
            )
        )
        print("Complete profile pending reminder email")
    except Exception as e:
        print("Failed to send profile completion email with error: {}".format(str(e)))


@periodic_task(run_every=(crontab(minute='*/2')), name="vendor_checkin_reminder_notification")
def task_vendor_checkin_reminder_notification():
    """
        Task to send out notifications to vendors to remind them to checkin if they have not checked in
        15 minutes after their documented opening time
        Runs every 2 minutes
    """
    try:
        users = User.filter.with_user_local_date_time().prefetch_related(
            'vendor',
            'vendor__business'
        ).filter(
            vendor__notification_preference__checkin_checkout=True,
            vendor__business__open=False,
            vendor__business__opening_hours__weekday=timezone.now().weekday(),
            vendor__business__opening_hours__from_hour__gte=(F('check_in_time_before')),
            vendor__business__opening_hours__from_hour__lt=(F('check_in_time_after')))

        notification_text = "Reminder to checkin for today!"
        data = {
            "type": CHECKIN_CHECKOUT,
            "title": ""
        }
        for user in users:
            send_message_to_devices(enums.VENDOR,
                                    user.devices.all(),
                                    notification_text,
                                    data,
                                    unread_count(user))
        if settings.DEBUG:
            print("Checkin reminder notification sent to devices: {}".format(
                list(users.values_list('id', flat=True))
            ))
        else:
            print("Checkin reminder notification sent to vendors")
    except Exception as e:
        print("Failed to send checkin reminder notification with error: {}".format(str(e)))


@periodic_task(run_every=(crontab(minute='*/2')), name="vendor_checkout_reminder_notification")
def task_vendor_checkout_reminder():
    """
        Task to send out notifications 15 minutes prior to vendors checkout time
        Runs every 2 minutes
    """
    try:
        users = User.filter.with_user_local_date_time().prefetch_related(
            'vendor',
            'vendor__business'
        ).filter(
            vendor__notification_preference__checkin_checkout=True,
            vendor__business__open=True,
            vendor__business__check_out__gte=(F('check_out_time_before')),
            vendor__business__check_out__lt=(F('check_out_time_after'))
        )
        notification_text = "You will be checked out in 15 minutes!"
        data = {
            "type": CHECKIN_CHECKOUT,
            "title": ""
        }
        for user in users:
            send_message_to_devices(enums.VENDOR,
                                    user.devices.all(),
                                    notification_text,
                                    data,
                                    unread_count(user))
        if settings.DEBUG:
            print("Checkout reminder notification sent to devices: {}".format(
                list(users.values_list('id', flat=True))
            ))
        else:
            print("Checkout reminder notification sent to vendors")

    except Exception as e:
        print("Failed to send checkout reminder notification with error: {}".format(str(e)))


@periodic_task(run_every=(crontab(minute='*/1')), name="vendor_checkout")
def task_vendor_checkout():
    """
        Task to checkout vendors
        Runs every minute
    """
    try:
        business = Business.objects.with_user_local_date_time().filter(
            check_out__gt=(F('auto_check_out_time_before')),
            check_out__lte=(F('auto_check_out_time_after')),
            open=True
        )
        Dish.objects.filter(temporary_price__gt=0, business__in=business).update(temporary_price=0)
        business.update(
            open=False,
            check_out=None,
            offer_active=False,
            discount_active=False
        )
        if settings.DEBUG:
            print(business)
            print("Auto checkout of vendors with business open")
        else:
            print("Auto checkout of vendors successful")

    except Exception as e:
        print("Failed to auto checkout vendors: {}".format(str(e)))
