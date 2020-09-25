import json

from django.utils import timezone

from seller.notification import constants, enums as notification_enums
from seller.notification.models import Notifications
from seller.notification.email import HawkkerEmailMessage
from seller.notification.utils import create_notifications
from seller.notification.utils import send_message_to_devices
from seller.user.utils import enums
from seller.vendor.utils import send_support_email


def unread_count(user):
    message_count = Notifications.objects.for_user(user).with_unread().count()
    return message_count


def send_push_notification_eater(user, transaction):
    data = {}
    notification_text = "{} Points have been spent.".format(transaction.coins)
    context = {"vendor_uuid": str(user.vendor.uuid),
               "transaction": transaction.id,
               "coins": transaction.coins,
               "business_name": user.vendor.business.name,
               "type": constants.EATER_REDEEMPTION,
               "title": ""}

    data['context'] = json.dumps(context)
    data['message'] = notification_text
    create_notifications(
        user=transaction.user,
        content_object=transaction,
        notification_type=constants.EATER_REDEEMPTION,
        **data
    )
    badge_count = unread_count(transaction.user)
    send_message_to_devices(
        enums.EATER,
        transaction.user.devices.all(),
        notification_text,
        context,
        badge_count
    )


def send_report_vendor_email(subject, text, vendor, eater):
    date = timezone.now().time().strftime('%H:%M')
    time = timezone.now().date()

    # Send a nicely formatted html email to user
    HawkkerEmailMessage(
        email_type=notification_enums.REPORT_VENDOR,
        template_name='templated_email/vendor_report.email',
        context={
            'vendor': vendor,
            'eater': eater,
            'date': date,
            'time': time,
            'comment': text,
            'reason': subject,
        }).send(to=[eater.email])

    message = "Vendor Report\nVendor Details: {} \n\n Eater Deatails:{} \n\n Location:{},{} \n\n " \
              "Time:{}\n\n Date:{} \n\n Comment:{} \n\n " \
              "".format('{} email: {}'.format(vendor.name, vendor.email),
                        eater.name,
                        vendor.location.x,
                        vendor.location.y,
                        date,
                        time,
                        text)
    # Do not send this to the user. We send them a nicer email
    send_support_email(subject, message, [])


def send_support_vendor_email(subject, message, users_emails, eater):
    # Send a nicely formatted html email to user
    HawkkerEmailMessage(
        email_type=notification_enums.SUPPORT,
        template_name='templated_email/support.email',
        context={
            'subect': subject,
            'comment': message,
        }).send(to=users_emails)

    # Do not send this to the user. We send them a nicer email
    send_support_email(subject, 'Support Message\n\nFrom: {}\nMessage: {}'.format(
        eater.email, message), [])
