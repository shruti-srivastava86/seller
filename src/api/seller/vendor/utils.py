from django.conf import settings
from rest_framework.pagination import PageNumberPagination

from api.generics.utils import send_mail
from seller.authentication.token import get_token
from seller.chat.models import Message
from seller.notification import enums
from seller.notification.email import HawkkerEmailMessage


def send_email(subject, message, emails):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.DEFAULT_FROM_EMAIL],
        bcc=emails
    )


def send_support_email(subject, message, emails):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_SUPPORT_EMAIL,
        recipient_list=[settings.DEFAULT_SUPPORT_EMAIL],
        bcc=emails
    )


def send_account_approved_email(vendors):
    for vendor in vendors:
        HawkkerEmailMessage(
            email_type=enums.APPROVE_EMAIL,
            template_name='templated_email/approved.email',
            context={
                'link': settings.WEB_BASE_URL,
                'vendor': vendor,
            }).send(to=[vendor.email])


def send_account_rejected_email(vendors):
    for vendor in vendors:
        HawkkerEmailMessage(
            email_type=enums.REJECT_EMAIL,
            template_name='templated_email/rejected.email',
            context={
                'link': settings.WEB_BASE_URL,
                'vendor': vendor,
            }).send(to=[vendor.email])


def send_on_board_email(vendor):
    HawkkerEmailMessage(
        email_type=enums.ONBOARDING,
        template_name='templated_email/onboarding.email',
        context={
            'link': '{}/create-profile?token={}'.format(
                settings.WEB_BASE_URL,
                get_token(vendor)),
            'vendor': vendor,
        }).send(to=[vendor.email])


def send_profile_complete_reminder_email(users):
    for user in users:
        HawkkerEmailMessage(
            email_type=enums.REMIND_COMPLETE,
            template_name='templated_email/remind_complete.email',
            context={
                'link': '{}/create-profile?token={}'.format(
                    settings.WEB_BASE_URL,
                    get_token(user)),
            }).send(to=[user.email])


def unread_count(user):
    message_count = Message.objects.for_user(user).unread(user).count()
    return message_count


def unread_count_conversation(user, chat):
    message_count = Message.objects. \
        for_user(user). \
        filter(conversation__chat_type=chat). \
        unread(user). \
        count()
    return message_count


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 10000
