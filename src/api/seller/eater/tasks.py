import json
from datetime import datetime
from datetime import timedelta

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from seller.eater.utils import unread_count
from seller.notification import constants
from seller.notification.utils import create_notifications
from seller.notification.utils import send_message_to_devices
from seller.purchase.models import Purchase
from seller.user import enums
from seller.user.validators import Validations


@periodic_task(run_every=(crontab(minute='*/1')), name="eater_review_notification")
def task_eater_review_notification():
    """
    Task to send notification to eater after the purchase is completed
    :return:
    """
    general_settings = Validations.validate_general_settings()
    try:
        purchases = Purchase.objects.filter(
            created_at__gt=(
                    datetime.now() - timedelta(minutes=(general_settings.eater_review_reminder + 1))),
            created_at__lte=(
                    datetime.now() - timedelta(minutes=general_settings.eater_review_reminder)),
        )

        for purchase in purchases:
            data = {}
            notification_text = "How was {}".format(purchase.vendor.business.name)

            context = {
                "type": constants.EATER_REVIEW,
                "vendor": purchase.vendor.id,
                "vendor_uuid": str(purchase.vendor.uuid),
                "businesss_name": purchase.vendor.business.name,
                "purchase": purchase.id,
                "title": ""

            }

            data['context'] = json.dumps(context)
            data['message'] = notification_text
            # data['title'] = notification_text
            create_notifications(
                user=purchase.eater,
                content_object=purchase,
                notification_type=constants.EATER_REVIEW,
                **data
            )
            badge_count = unread_count(purchase.eater)

            if purchase.eater.notification_preference.review:

                send_message_to_devices(enums.EATER,
                                        purchase.eater.devices.all(),
                                        notification_text,
                                        context,
                                        badge_count)

                if settings.DEBUG:
                    print("Reminder to leave review sent to purchase")
                    print(purchases)

                else:
                    print("Reminder to leave review sent to vendors")
    except Exception as e:
        print("Failed to send leave review reminder notification with error: {}".format(str(e)))
